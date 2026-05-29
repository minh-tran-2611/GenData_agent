"""SQL sink: turn simulated customers/orders into INSERT statements appended to
the MySQL dump file. Uses explicit IDs from a base offset so foreign keys wire
up deterministically inside a static .sql file. Each day is one self-contained
block wrapped in FOREIGN_KEY_CHECKS=0/1 so it can be run (or commented) on its own.
"""
import random
from datetime import datetime, timedelta
from typing import Any, Optional

DEFAULT_ID_BASE = 100000
# BCrypt hash of "Simulated@123" (cost 10) — Spring BCryptPasswordEncoder compatible.
DEFAULT_PASSWORD_HASH = "$2b$10$Xy70A0VtEsp05uopohQH..HzAc8.5V.ptDmtVhLC6rw6qQwY6OTea"
DEFAULT_PASSWORD_PLAINTEXT = "Simulated@123"

DEFAULT_ADDRESS = {
    "address": "123 Đường Mô Phỏng",
    "ward": "Phường 1",
    "district": "Quận 1",
    "province": "TP. Hồ Chí Minh",
}

# --- Pools to make simulated identities/addresses varied but plausible (HCMC) ---
_LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ",
               "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
_MIDDLE_M = ["Văn", "Hữu", "Đức", "Minh", "Quang", "Gia", "Bảo", "Tuấn", "Anh", "Hoàng"]
_MIDDLE_F = ["Thị", "Ngọc", "Thanh", "Thu", "Hoài", "Khánh", "Mai", "Phương", "Diễm"]
_FIRST_M = ["An", "Bình", "Dũng", "Hùng", "Khoa", "Long", "Nam", "Phúc", "Quân",
            "Sơn", "Trung", "Tú", "Hải", "Đạt", "Kiên", "Thành"]
_FIRST_F = ["Châu", "Giang", "Hà", "Hân", "Hương", "Lan", "Linh", "Mai", "Nga",
            "Nhung", "Tâm", "Thảo", "Trang", "Vy", "Yến", "Quỳnh"]
_PHONE_PREFIXES = ["32", "33", "34", "35", "36", "37", "38", "39", "70", "76", "77",
                   "78", "79", "81", "82", "83", "84", "85", "88", "90", "91", "93",
                   "94", "96", "97", "98"]
_STREETS = ["Lê Lợi", "Nguyễn Huệ", "Hai Bà Trưng", "Cách Mạng Tháng 8", "Điện Biên Phủ",
            "Nguyễn Thị Minh Khai", "Trần Hưng Đạo", "Lý Tự Trọng", "Pasteur",
            "Nam Kỳ Khởi Nghĩa", "Võ Văn Tần", "Cao Thắng", "Lê Văn Sỹ",
            "Phan Xích Long", "Nguyễn Trãi", "Sư Vạn Hạnh", "Ba Tháng Hai"]
_WARDS = ["Phường Bến Nghé", "Phường Bến Thành", "Phường Đa Kao", "Phường Cầu Ông Lãnh",
          "Phường Phạm Ngũ Lão", "Phường 1", "Phường 2", "Phường 5", "Phường 7",
          "Phường 12", "Phường 14", "Phường 25"]
_DISTRICTS = ["Quận 1", "Quận 3", "Quận 5", "Quận 10", "Quận Bình Thạnh",
              "Quận Phú Nhuận", "Quận Tân Bình", "Quận Gò Vấp", "Thành phố Thủ Đức"]
_PROVINCE = "TP. Hồ Chí Minh"

# Hour-of-day weights for a restaurant: lunch (11-13) and dinner (18-21) peaks.
_HOUR_WEIGHTS = {7: 1, 8: 2, 9: 2, 10: 3, 11: 7, 12: 10, 13: 8, 14: 3, 15: 2,
                 16: 3, 17: 5, 18: 9, 19: 10, 20: 8, 21: 5, 22: 2}


def _random_person() -> tuple[str, str]:
    """Return (full_name, gender) — a plausible Vietnamese name with matching gender."""
    if random.random() < 0.5:
        gender = "MALE"
        name = f"{random.choice(_LAST_NAMES)} {random.choice(_MIDDLE_M)} {random.choice(_FIRST_M)}"
    else:
        gender = "FEMALE"
        name = f"{random.choice(_LAST_NAMES)} {random.choice(_MIDDLE_F)} {random.choice(_FIRST_F)}"
    return name, gender


def _random_address() -> dict[str, str]:
    return {
        "address": f"{random.randint(1, 450)} {random.choice(_STREETS)}",
        "ward": random.choice(_WARDS),
        "district": random.choice(_DISTRICTS),
        "province": _PROVINCE,
    }


def _s(v: Any) -> str:
    """Quote a string value (or NULL)."""
    if v is None:
        return "NULL"
    s = str(v).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"


def _n(v: Any) -> str:
    """Numeric literal (or NULL)."""
    if v is None:
        return "NULL"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "NULL"
    return str(int(f)) if f.is_integer() else repr(round(f, 2))


def _dt(dt: datetime) -> str:
    return f"'{dt.strftime('%Y-%m-%d %H:%M:%S.%f')}'"


def _parse_date(value: Optional[str]) -> datetime:
    if value:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    today = datetime.now()
    return datetime(today.year, today.month, today.day)


def _parse_any_dt(value: Any) -> Optional[datetime]:
    """Parse a datetime from common API/DB string shapes; returns None if unknown."""
    if not value:
        return None
    s = str(value).strip().replace("T", " ")
    if s.endswith("Z"):
        s = s[:-1]
    s = s.split("+")[0].strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def compute_discount(voucher: dict, subtotal: float) -> float:
    """Discount applied to order total based on voucher type. Accepts snake or camelCase keys."""
    if not voucher:
        return 0.0
    vtype = voucher.get("type") or voucher.get("voucherType")
    val = float(voucher.get("discount_value") or voucher.get("discountValue") or 0)
    min_order = float(voucher.get("min_order_value") or voucher.get("minOrderValue") or 0)
    max_disc = voucher.get("max_discount_amount")
    if max_disc is None:
        max_disc = voucher.get("maxDiscountAmount")
    if subtotal < min_order:
        return 0.0
    if vtype == "PERCENTAGE":
        d = subtotal * val / 100.0
        if max_disc is not None:
            d = min(d, float(max_disc))
        return round(d, 2)
    if vtype == "FIXED_AMOUNT":
        return round(min(val, subtotal), 2)
    # FREE_SHIPPING affects shipping, not order discount_amount
    return 0.0


class SqlSink:
    def __init__(self, file_path: str, state: dict, config: dict):
        self.file_path = file_path
        self.state = state  # persisted: next_ids, user_seq, header_written
        self.id_base = int(config.get("id_base") or DEFAULT_ID_BASE)
        self.password_hash = config.get("password_hash") or DEFAULT_PASSWORD_HASH
        self.start_date = _parse_date(config.get("start_date"))
        self.vat_rate = float(config.get("vat_rate") or 0.0)
        self.shipping_fee = float(config.get("shipping_fee") or 0.0)
        self.addr = {**DEFAULT_ADDRESS, **(config.get("address") or {})}
        self._fixed_addr = bool(config.get("address"))  # honor an explicit address override
        self._buf: list[str] = []
        self._cur_date = self.start_date
        # Per-run customer profiles (name/phone/address/created) for consistent reuse.
        self._profiles: dict[int, dict] = {}
        self._hours = list(_HOUR_WEIGHTS.keys())
        self._hour_w = list(_HOUR_WEIGHTS.values())

    # ---- id / time helpers ----
    def _next(self, table: str) -> int:
        ids = self.state.setdefault("next_ids", {})
        cur = ids.get(table, self.id_base)
        ids[table] = cur + 1
        return cur

    def _ts(self) -> datetime:
        """A timestamp on the current day, weighted toward lunch/dinner peaks."""
        hour = random.choices(self._hours, weights=self._hour_w, k=1)[0]
        return datetime(self._cur_date.year, self._cur_date.month, self._cur_date.day,
                        hour, random.randint(0, 59), random.randint(0, 59))

    # ---- file / block lifecycle ----
    def ensure_header(self) -> None:
        if self.state.get("header_written"):
            return
        header = (
            "\n\n-- ============================================================\n"
            "-- SIMULATED DATA — generated by Data Generator Agent\n"
            f"-- explicit IDs from base {self.id_base}; seed password: {DEFAULT_PASSWORD_PLAINTEXT}\n"
            "-- ============================================================\n"
        )
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(header)
        self.state["header_written"] = True

    def begin_day(self, day: int) -> None:
        self._cur_date = self.start_date + timedelta(days=day - 1)
        self._buf = [
            "",
            f"-- ===== Ngày {day}: {self._cur_date.strftime('%Y-%m-%d')} =====",
            "SET FOREIGN_KEY_CHECKS=0;",
        ]

    # ---- identity helpers ----
    def _profile_for(self, uid: int) -> dict:
        """Stable per-customer name/phone/address within a run (for order receiver fields)."""
        prof = self._profiles.get(uid)
        if prof is None:
            name, _ = _random_person()
            phone = "0" + random.choice(_PHONE_PREFIXES) + f"{random.randint(0, 9_999_999):07d}"
            prof = {"name": name, "phone": phone,
                    "addr": self.addr if self._fixed_addr else _random_address(),
                    "created": None}
            self._profiles[uid] = prof
        return prof

    def end_day(self) -> None:
        self._buf.append("SET FOREIGN_KEY_CHECKS=1;")
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write("\n".join(self._buf) + "\n")
        self._buf = []

    # ---- row builders ----
    def add_customer(self, full_name: Optional[str] = None, gender: Optional[str] = None) -> int:
        seq = self.state.get("user_seq", 0) + 1
        self.state["user_seq"] = seq
        uid = self._next("users")
        # email/phone stay deterministic so the UNIQUE constraints never collide.
        email = f"sim_user_{seq}@example.com"
        phone = f"09{seq:09d}"
        created = self._ts()
        # Generate a plausible person; honor an explicitly-passed name/gender if given.
        gen_name, gen_gender = _random_person()
        full_name = full_name or gen_name
        gender = gender if gender in ("MALE", "FEMALE", "OTHER") else gen_gender
        # Cache the profile so this customer's orders reuse the same identity/address.
        self._profiles[uid] = {
            "name": full_name, "phone": phone,
            "addr": self.addr if self._fixed_addr else _random_address(),
            "created": created,
        }
        self._buf.append(
            "INSERT INTO `users` "
            "(`role`,`id`,`created_at`,`date_of_birth`,`email`,`full_name`,`gender`,`password`,"
            "`phone_number`,`status`,`total_spent`,`avatar_id`,`default_address_id`) VALUES "
            f"('CUSTOMER',{uid},{_dt(created)},NULL,{_s(email)},{_s(full_name)},{_s(gender)},"
            f"{_s(self.password_hash)},{_s(phone)},'ACTIVE',0,NULL,NULL);"
        )
        cart_id = self._next("carts")
        self._buf.append(
            f"INSERT INTO `carts` (`id`,`total_price`,`user_id`) VALUES ({cart_id},0,{uid});"
        )
        return uid

    def _voucher_eligible(self, voucher: dict, subtotal: float, user_id: int) -> bool:
        """Check status, validity window (vs simulated day), min order, usage limits."""
        status = voucher.get("status") or voucher.get("voucherStatus")
        if status and str(status).upper() != "ACTIVE":
            return False
        start = _parse_any_dt(voucher.get("startDate") or voucher.get("start_date"))
        end = _parse_any_dt(voucher.get("endDate") or voucher.get("end_date"))
        if start and self._cur_date.date() < start.date():
            return False
        if end and self._cur_date.date() > end.date():
            return False
        min_order = float(voucher.get("minOrderValue") or voucher.get("min_order_value") or 0)
        if subtotal < min_order:
            return False
        vid = voucher.get("id")
        if vid is None:
            return True
        limit = voucher.get("usageLimit")
        if limit is None:
            limit = voucher.get("usage_limit")
        existing = voucher.get("usedCount")
        if existing is None:
            existing = voucher.get("used_count") or 0
        ours = self.state.get("voucher_used", {}).get(str(vid), 0)
        if limit is not None and (int(existing) + ours) >= int(limit):
            return False
        per_user = voucher.get("usageLimitPerUser")
        if per_user is None:
            per_user = voucher.get("usage_limit_per_user")
        if per_user is not None:
            key = f"{vid}:{user_id}"
            if self.state.get("voucher_user_used", {}).get(key, 0) >= int(per_user):
                return False
        return True

    def _record_voucher_use(self, vid: Any, user_id: int) -> None:
        used = self.state.setdefault("voucher_used", {})
        used[str(vid)] = used.get(str(vid), 0) + 1
        per = self.state.setdefault("voucher_user_used", {})
        key = f"{vid}:{user_id}"
        per[key] = per.get(key, 0) + 1

    def add_order(
        self,
        user_id: int,
        items: list[dict],
        voucher: Optional[dict] = None,
        payment_method: str = "COD",
    ) -> dict:
        """items: [{product_id|combo_id, quantity, price}]. Returns summary dict."""
        prof = self._profile_for(user_id)
        created = self._ts()
        # An order can't predate the account's creation on the same day; nudge it a
        # little later but keep it within service hours (cap ~22:59).
        reg = prof.get("created")
        if reg is not None and created < reg:
            created = min(reg + timedelta(minutes=random.randint(5, 60)),
                          datetime(self._cur_date.year, self._cur_date.month, self._cur_date.day, 22, 59, 59))
        subtotal = sum(float(it["price"]) * int(it["quantity"]) for it in items)
        applied = voucher if (voucher and self._voucher_eligible(voucher, subtotal, user_id)) else None
        discount = compute_discount(applied, subtotal) if applied else 0.0
        voucher_id = applied.get("id") if applied else None
        free_ship = bool(applied and (applied.get("type") or applied.get("voucherType")) == "FREE_SHIPPING")
        shipping = 0.0 if free_ship else self.shipping_fee
        vat = round(subtotal * self.vat_rate, 2) if self.vat_rate else 0.0
        total = max(subtotal - discount, 0.0) + shipping + vat

        pay_id = self._next("payments")
        self._buf.append(
            "INSERT INTO `payments` (`id`,`amount`,`payment_date`,`payment_info`,`payment_message`,"
            "`payment_method`,`status`) VALUES "
            f"({pay_id},{_n(total)},{_dt(created)},NULL,'Simulated payment',{_s(payment_method)},'PAID');"
        )

        order_id = self._next("orders")
        a = prof["addr"]
        self._buf.append(
            "INSERT INTO `orders` "
            "(`id`,`created_at`,`discount_amount`,`address`,`district`,`is_default`,`province`,"
            "`receiver_name`,`receiver_phone`,`ward`,`shipping_fee`,`status`,`total_price`,"
            "`updated_at`,`vat`,`payment_id`,`user_id`,`voucher_id`) VALUES "
            f"({order_id},{_dt(created)},{_n(discount)},{_s(a['address'])},{_s(a['district'])},b'0',"
            f"{_s(a['province'])},{_s(prof['name'])},{_s(prof['phone'])},{_s(a['ward'])},{_n(shipping)},"
            f"'COMPLETED',{_n(total)},{_dt(created)},{_n(vat)},{pay_id},{user_id},"
            f"{_n(voucher_id) if voucher_id else 'NULL'});"
        )

        # Keep users.total_spent consistent so analytics/reports see realistic lifetime spend.
        self._buf.append(
            f"UPDATE `users` SET `total_spent`=COALESCE(`total_spent`,0)+{_n(total)} WHERE `id`={user_id};"
        )

        for it in items:
            item_id = self._next("order_items")
            combo_id = it.get("combo_id")
            product_id = it.get("product_id")
            combo_sql = str(int(combo_id)) if combo_id else "NULL"
            product_sql = str(int(product_id)) if product_id else "NULL"
            self._buf.append(
                "INSERT INTO `order_items` (`id`,`created_at`,`note`,`price`,`quantity`,`reviewed`,"
                "`updated_at`,`combo_id`,`order_id`,`order_at_table_id`,`place_table_id`,`product_id`) VALUES "
                f"({item_id},{_dt(created)},NULL,{_n(it['price'])},{int(it['quantity'])},b'0',"
                f"{_dt(created)},{combo_sql},{order_id},NULL,NULL,{product_sql});"
            )

        # Record voucher usage when a voucher was actually applied (free-ship counts
        # even though order discount_amount is 0 — the saving is the shipping fee).
        if voucher_id and (discount > 0 or free_ship):
            vu_discount = self.shipping_fee if free_ship else discount
            vu_id = self._next("voucher_usages")
            self._buf.append(
                "INSERT INTO `voucher_usages` (`id`,`discount_amount`,`used_at`,`order_id`,`user_id`,"
                f"`voucher_id`) VALUES ({vu_id},{_n(vu_discount)},{_dt(created)},{order_id},{user_id},{int(voucher_id)});"
            )
            self._buf.append(
                f"UPDATE `vouchers` SET `used_count`=`used_count`+1 WHERE `id`={int(voucher_id)};"
            )
            self._record_voucher_use(voucher_id, user_id)

        return {
            "order_id": order_id,
            "subtotal": round(subtotal, 2),
            "discount": discount,
            "total": round(total, 2),
            "num_items": len(items),
        }
