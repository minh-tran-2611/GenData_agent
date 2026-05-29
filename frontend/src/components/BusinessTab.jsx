import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const BLANK = {
  name: "", business_type: "", description: "",
  open_date: "", location: "", base_url: "", notes: "",
};
const BLANK_GROWTH = { mode: "day", start_orders_per_day: 10, monthly_growth_rate: 0.15, plateau_at_month: 12, new_user_ratio: 0.3 };

export default function BusinessTab() {
  const [biz, setBiz] = useState(BLANK);
  const [growth, setGrowth] = useState(BLANK_GROWTH);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const b = await api.getBusiness();
        const g = await api.getGrowth();
        setBiz({ ...BLANK, ...b });
        setGrowth({ ...BLANK_GROWTH, ...g });
      } catch (e) { setMsg(e.message); }
    })();
  }, []);

  const save = async () => {
    setMsg("");
    try {
      await api.setBusiness(biz);
      await api.setGrowth(growth);
      setMsg("Đã lưu.");
    } catch (e) { setMsg(e.message); }
  };

  const f = (k) => (e) => setBiz({ ...biz, [k]: e.target.value });
  const gf = (k, isNum = false) => (e) => setGrowth({ ...growth, [k]: isNum ? Number(e.target.value) : e.target.value });

  return (
    <div className="space-y-4 max-w-3xl">
      <div className="card">
        <h2 className="text-lg font-semibold mb-3">Thông tin doanh nghiệp</h2>
        <p className="text-xs text-slate-400 mb-3">
          Orchestrator dùng thông tin này để phân tích → quyết định tệp khách hàng phù hợp.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="label">Tên doanh nghiệp</label>
            <input className="input" value={biz.name} onChange={f("name")} placeholder="VD: Cà phê Bụi" />
          </div>
          <div>
            <label className="label">Loại hình</label>
            <input className="input" value={biz.business_type} onChange={f("business_type")} placeholder="quán cà phê / nhà hàng / shop quần áo..." />
          </div>
          <div className="md:col-span-2">
            <label className="label">Mô tả chi tiết</label>
            <textarea className="input" rows="3" value={biz.description} onChange={f("description")} placeholder="Doanh nghiệp bán gì, phân khúc giá, khách hàng mục tiêu là ai..." />
          </div>
          <div>
            <label className="label">Ngày mở cửa</label>
            <input type="date" className="input" value={biz.open_date} onChange={f("open_date")} />
          </div>
          <div>
            <label className="label">Địa điểm</label>
            <input className="input" value={biz.location} onChange={f("location")} placeholder="Quận 1, TP.HCM" />
          </div>
          <div className="md:col-span-2">
            <label className="label">Base URL API (tùy chọn — dùng khi endpoint URL bắt đầu bằng /)</label>
            <input className="input" value={biz.base_url} onChange={f("base_url")} placeholder="https://api.example.com" />
          </div>
          <div className="md:col-span-2">
            <label className="label">Ghi chú thêm</label>
            <textarea className="input" rows="2" value={biz.notes} onChange={f("notes")} placeholder="Giờ cao điểm, khuyến mãi đặc biệt, đặc thù khác..." />
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-3">Growth config</h2>
        <p className="text-xs text-slate-400 mb-3">Tham khảo cho Orchestrator. Agent có thể tự điều chỉnh theo ngày cụ thể.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="label">Mode</label>
            <select className="input" value={growth.mode} onChange={gf("mode")}>
              <option value="day">Theo ngày (chi tiết nhất)</option>
              <option value="month">Theo tháng (batch, rẻ)</option>
              <option value="year">Theo năm (seed nhanh)</option>
            </select>
          </div>
          <div>
            <label className="label">Đơn hàng/ngày khởi điểm</label>
            <input type="number" className="input" value={growth.start_orders_per_day} onChange={gf("start_orders_per_day", true)} />
          </div>
          <div>
            <label className="label">Tăng trưởng / tháng (0-1)</label>
            <input type="number" step="0.01" className="input" value={growth.monthly_growth_rate} onChange={gf("monthly_growth_rate", true)} />
          </div>
          <div>
            <label className="label">Bão hòa ở tháng thứ</label>
            <input type="number" className="input" value={growth.plateau_at_month} onChange={gf("plateau_at_month", true)} />
          </div>
          <div>
            <label className="label">Tỉ lệ user mới (0-1)</label>
            <input type="number" step="0.05" className="input" value={growth.new_user_ratio} onChange={gf("new_user_ratio", true)} />
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="btn-primary" onClick={save}>Lưu</button>
        {msg && <span className="text-xs text-slate-400">{msg}</span>}
      </div>
    </div>
  );
}
