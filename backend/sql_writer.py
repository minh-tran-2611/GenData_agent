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

# Đặt bàn (place_table): phần lớn hoàn tất, ít bị huỷ/chờ. Khớp EPlaceTableStatus.
_BOOKING_STATUS = ["COMPLETED", "CONFIRMED", "PENDING", "DENIED"]
_BOOKING_STATUS_W = [70, 18, 7, 5]
_BOOKING_NOTES = [None, None, None, "Gần cửa sổ", "Khu yên tĩnh", "Có trẻ em",
                  "Tiệc sinh nhật", "Bàn riêng tư", "Kỷ niệm"]
_MEMBER_POOL = [2, 2, 2, 4, 4, 4, 5, 6, 8]

# Nội dung review theo số sao (review thật lệch về tích cực). Dùng cho bảng reviews.
_REVIEW_CONTENT = {
    5: ["Món ăn rất ngon, sẽ quay lại!", "Tuyệt vời, đúng vị, phục vụ nhanh.",
        "Chất lượng xuất sắc, đáng tiền.", "Ngon, trình bày đẹp, rất hài lòng.",
        "Best seller đúng nghĩa, 10 điểm."],
    4: ["Ngon, sẽ ủng hộ tiếp.", "Khá ổn, giao hàng nhanh.", "Hợp khẩu vị, giá hợp lý.",
        "Tốt, chỉ hơi ít topping."],
    3: ["Tạm ổn, không có gì đặc biệt.", "Bình thường, đủ ăn.",
        "Ổn nhưng hơi nguội khi nhận.", "Trung bình, có thể cải thiện."],
    2: ["Hơi nhạt, chưa hài lòng.", "Giao hơi lâu, món nguội.",
        "Không như kỳ vọng.", "Phần ăn hơi ít so với giá."],
    1: ["Thất vọng, sẽ không đặt lại.", "Món không ngon, đóng gói tệ.",
        "Chất lượng kém.", "Rất tệ."],
}
_REVIEW_RATES = [5, 4, 3, 2, 1]
_REVIEW_RATE_W = [50, 30, 12, 5, 3]


def _pick_order_outcome(payment_method: str, dine_in: bool = False) -> dict:
    """Chọn (trạng thái đơn, trạng thái payment, có tính doanh thu) sát thực tế.

    Phần lớn COMPLETED/PAID; có 1 tỉ lệ huỷ (FAIL = huỷ trước trả, REFUND = đã trả rồi hoàn)
    và vài đơn đang dang dở (PENDING / WAITING_FOR_PAYMENT). COD không có 'chờ thanh toán online'.
    """
    if dine_in:
        status = random.choices(["COMPLETED", "CANCELED", "PENDING"], weights=[93, 5, 2], k=1)[0]
    else:
        status = random.choices(
            ["COMPLETED", "CANCELED", "PENDING", "WAITING_FOR_PAYMENT"],
            weights=[84, 10, 4, 2], k=1)[0]
    if status == "WAITING_FOR_PAYMENT" and payment_method != "MOMO":
        status = "PENDING"
    if status == "COMPLETED":
        return {"order_status": "COMPLETED", "payment_status": "PAID", "revenue": True}
    if status == "CANCELED":
        pay = random.choices(["FAIL", "REFUND"], weights=[55, 45], k=1)[0]
        return {"order_status": "CANCELED", "payment_status": pay, "revenue": False}
    if status == "WAITING_FOR_PAYMENT":
        return {"order_status": "WAITING_FOR_PAYMENT", "payment_status": "PROCESSING", "revenue": False}
    return {"order_status": "PENDING", "payment_status": "PROCESSING", "revenue": False}


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
        # Tỉ lệ món (của đơn thành công) được khách đánh giá -> sinh review + rating.
        self.review_rate = float(config.get("review_rate", 0.35))
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
            "name": full_name, "phone": phone, "email": email,
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

        # Trạng thái đơn + payment sát thực tế (đa số COMPLETED, vài huỷ/dang dở).
        outcome = _pick_order_outcome(payment_method)
        pay_id = self._next("payments")
        self._buf.append(
            "INSERT INTO `payments` (`id`,`amount`,`payment_date`,`payment_info`,`payment_message`,"
            "`payment_method`,`status`) VALUES "
            f"({pay_id},{_n(total)},{_dt(created)},NULL,'Simulated payment',{_s(payment_method)},"
            f"{_s(outcome['payment_status'])});"
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
            f"{_s(outcome['order_status'])},{_n(total)},{_dt(created)},{_n(vat)},{pay_id},{user_id},"
            f"{_n(voucher_id) if voucher_id else 'NULL'});"
        )

        # Chỉ cộng total_spent khi đơn thực sự thành công (COMPLETED + PAID).
        if outcome["revenue"]:
            self._buf.append(
                f"UPDATE `users` SET `total_spent`=COALESCE(`total_spent`,0)+{_n(total)} WHERE `id`={user_id};"
            )

        for it in items:
            item_id = self._next("order_items")
            combo_id = it.get("combo_id")
            product_id = it.get("product_id")
            combo_sql = str(int(combo_id)) if combo_id else "NULL"
            product_sql = str(int(product_id)) if product_id else "NULL"
            # Một phần món của đơn thành công được khách đánh giá (review thật + rating).
            do_review = bool(outcome["revenue"] and product_id and random.random() < self.review_rate)
            reviewed_bit = "b'1'" if do_review else "b'0'"
            self._buf.append(
                "INSERT INTO `order_items` (`id`,`created_at`,`note`,`price`,`quantity`,`reviewed`,"
                "`updated_at`,`combo_id`,`order_id`,`order_at_table_id`,`place_table_id`,`product_id`) VALUES "
                f"({item_id},{_dt(created)},NULL,{_n(it['price'])},{int(it['quantity'])},{reviewed_bit},"
                f"{_dt(created)},{combo_sql},{order_id},NULL,NULL,{product_sql});"
            )
            if do_review:
                self._emit_review(order_item_id=item_id, product_id=int(product_id),
                                  user_id=user_id, base_dt=created)

        # Record voucher usage when a voucher was actually applied (free-ship counts
        # even though order discount_amount is 0 — the saving is the shipping fee).
        # Chỉ tính lượt dùng voucher cho đơn thành công (đơn huỷ -> voucher hoàn lại).
        if outcome["revenue"] and voucher_id and (discount > 0 or free_ship):
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

    # ---- shared emitters (payment + order items) -----------------------------
    def _emit_payment(self, total: float, created: datetime, method: str = "COD",
                      status: str = "PAID") -> int:
        """Emit a payment row; returns its id. EPaymentMethod chỉ có COD/MOMO."""
        if method not in ("COD", "MOMO"):
            method = "COD"
        pay_id = self._next("payments")
        self._buf.append(
            "INSERT INTO `payments` (`id`,`amount`,`payment_date`,`payment_info`,`payment_message`,"
            "`payment_method`,`status`) VALUES "
            f"({pay_id},{_n(total)},{_dt(created)},NULL,'Simulated payment',{_s(method)},{_s(status)});"
        )
        return pay_id

    def _emit_review(self, *, order_item_id: int, product_id: int, user_id: int,
                     base_dt: datetime) -> int:
        """Emit a review row (rating lệch tích cực) cho 1 order_item đã hoàn tất."""
        rate = random.choices(_REVIEW_RATES, weights=_REVIEW_RATE_W, k=1)[0]
        content = random.choice(_REVIEW_CONTENT[rate])
        # Khách thường đánh giá sau khi nhận hàng vài giờ → vài ngày.
        created = base_dt + timedelta(days=random.randint(0, 4), hours=random.randint(1, 12))
        rid = self._next("reviews")
        self._buf.append(
            "INSERT INTO `reviews` (`id`,`content`,`created_at`,`rate`,`updated_at`,"
            "`order_item_id`,`product_id`,`user_id`) VALUES "
            f"({rid},{_s(content)},{_dt(created)},{rate},{_dt(created)},"
            f"{int(order_item_id)},{int(product_id)},{int(user_id)});"
        )
        return rid

    def _emit_order_items(self, items: list[dict], created: datetime, *,
                          order_id: Optional[int] = None,
                          order_at_table_id: Optional[int] = None,
                          place_table_id: Optional[int] = None) -> None:
        """Emit order_items rows linked to exactly one parent (order / order-at-table / booking)."""
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
                f"{_dt(created)},{combo_sql},{order_id if order_id else 'NULL'},"
                f"{order_at_table_id if order_at_table_id else 'NULL'},"
                f"{place_table_id if place_table_id else 'NULL'},{product_sql});"
            )

    def _booking_times(self) -> tuple[datetime, datetime]:
        """(created, started): đặt lúc created, giờ ngồi started muộn hơn, cùng ngày, cap 22:30."""
        created = self._ts()
        day_end = datetime(self._cur_date.year, self._cur_date.month, self._cur_date.day, 22, 30, 0)
        started = min(created + timedelta(hours=random.randint(0, 4), minutes=random.choice([0, 30])), day_end)
        return created, started

    # ---- tables (seed once) --------------------------------------------------
    def ensure_tables(self, count: int = 15) -> list[int]:
        """Seed các bàn vật lý 1 lần duy nhất (idempotent qua state). Trả về list id bàn."""
        ids = self.state.get("table_ids")
        if ids:
            return ids
        ids, seats = [], []
        seats_pool = [2, 2, 4, 4, 4, 6, 8]
        created = datetime(self.start_date.year, self.start_date.month, self.start_date.day, 8, 0, 0)
        for i in range(1, int(count) + 1):
            tid = self._next("tables")
            seat = random.choice(seats_pool)
            self._buf.append(
                "INSERT INTO `tables` (`id`,`created_at`,`qr`,`seat`,`table_number`,`updated_at`) VALUES "
                f"({tid},{_dt(created)},NULL,{seat},{_s(f'Bàn {i}')},{_dt(created)});"
            )
            ids.append(tid)
            seats.append(seat)
        self.state["table_ids"] = ids
        self.state["table_seats"] = seats
        return ids

    # ---- đặt bàn khách vãng lai ----------------------------------------------
    def add_guest_booking(self, status: Optional[str] = None) -> int:
        """place_table_guests: khách lẻ không tài khoản, CHỈ là yêu cầu giữ chỗ (không hoá đơn).

        status do simulator quyết theo sức chứa (DENIED khi hết chỗ); None = tự random.
        """
        name, _ = _random_person()
        phone = "0" + random.choice(_PHONE_PREFIXES) + f"{random.randint(0, 9_999_999):07d}"
        seq = self.state.get("guest_seq", 0) + 1
        self.state["guest_seq"] = seq
        email = f"guest_{seq}@example.com" if random.random() < 0.6 else None
        created, started = self._booking_times()
        status = status or random.choices(_BOOKING_STATUS, weights=_BOOKING_STATUS_W, k=1)[0]
        bid = self._next("place_table_guests")
        self._buf.append(
            "INSERT INTO `place_table_guests` (`id`,`created_at`,`email`,`fullname`,`member_int`,`note`,"
            "`phone_number`,`started_at`,`status`,`updated_at`) VALUES "
            f"({bid},{_dt(created)},{_s(email)},{_s(name)},{random.choice(_MEMBER_POOL)},"
            f"{_s(random.choice(_BOOKING_NOTES))},{_s(phone)},{_dt(started)},{_s(status)},{_dt(started)});"
        )
        return bid

    # ---- đặt bàn khách quen (có tài khoản, có thể gọi món trước) --------------
    def add_customer_booking(self, user_id: int, status: Optional[str] = None) -> int:
        """place_table_customers: khách quen (đã đăng nhập) gửi YÊU CẦU đặt bàn.

        Chỉ là bản ghi giữ chỗ — KHÔNG mang hoá đơn. Doanh thu dine-in (ăn tại bàn) hệ thống
        thật không quy được về khách quen (order_at_table ẩn danh), nên total_price/payment để
        NULL và KHÔNG cộng total_spent. status do simulator quyết theo sức chứa.
        """
        prof = self._profile_for(user_id)
        email = prof.get("email") or f"sim_user_{user_id}@example.com"
        created, started = self._booking_times()
        status = status or random.choices(_BOOKING_STATUS, weights=_BOOKING_STATUS_W, k=1)[0]
        bid = self._next("place_table_customers")
        self._buf.append(
            "INSERT INTO `place_table_customers` (`id`,`created_at`,`email`,`member`,`note`,`phone_number`,"
            "`started_at`,`status`,`total_price`,`updated_at`,`payment_id`,`user_id`) VALUES "
            f"({bid},{_dt(created)},{_s(email)},{random.choice(_MEMBER_POOL)},"
            f"{_s(random.choice(_BOOKING_NOTES))},{_s(prof['phone'])},{_dt(started)},{_s(status)},"
            f"NULL,{_dt(started)},NULL,{user_id});"
        )
        return bid

    # ---- order tại bàn (dine-in) ---------------------------------------------
    def add_order_at_table(self, table_id: int, items: list[dict],
                           payment_method: str = "COD") -> dict:
        """order_at_table: khách ngồi tại bàn gọi món (không phí ship). items đã resolve giá."""
        created = self._ts()
        subtotal = sum(float(it["price"]) * int(it["quantity"]) for it in items)
        vat = round(subtotal * self.vat_rate, 2) if self.vat_rate else 0.0
        total = round(subtotal + vat, 2)
        outcome = _pick_order_outcome(payment_method, dine_in=True)
        pay_id = self._emit_payment(total, created, payment_method, status=outcome["payment_status"])
        oid = self._next("order_at_table")
        self._buf.append(
            "INSERT INTO `order_at_table` (`id`,`created_at`,`table_id`,`status`,`total_price`,"
            "`updated_at`,`payment_id`) VALUES "
            f"({oid},{_dt(created)},{int(table_id)},{_s(outcome['order_status'])},{_n(total)},"
            f"{_dt(created)},{pay_id});"
        )
        self._emit_order_items(items, created, order_at_table_id=oid)
        return {"order_at_table_id": oid, "total": round(total, 2), "num_items": len(items)}
