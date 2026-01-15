import streamlit as st
import calendar
from datetime import date, datetime, timedelta

st.title("有休申請アプリ")

# 初期化
if "year" not in st.session_state:
    today = date.today()
    st.session_state.year = today.year
    st.session_state.month = today.month
if "reservations" not in st.session_state:
    # structure: { "A": {"YYYY-MM-DD": {"type":"AM/PM/全日", "comment": "..." } }, "B": {...}, "C": {...} }
    st.session_state.reservations = {"石塚久美子": {}, "伊藤つぐみ": {}, "大城敬子": {}}

# 簡易表示用の氏名短縮マップ
full_to_short = {"石塚久美子": "石塚", "伊藤つぐみ": "伊藤", "大城敬子": "大城"}

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

# ユーザー選択
applicant = st.radio("申請者を選択", ["石塚久美子", "伊藤つぐみ", "大城敬子"])

# 月ナビゲーション
col_prev, col_mid, col_next = st.columns([1,6,1])
with col_prev:
    if st.button("前月"):
        y, m = st.session_state.year, st.session_state.month
        prev = (date(y, m, 1) - timedelta(days=1))
        st.session_state.year, st.session_state.month = prev.year, prev.month
with col_mid:
    st.markdown(f"#### {st.session_state.year}年 {st.session_state.month}月")
with col_next:
    if st.button("翌月"):
        y, m = st.session_state.year, st.session_state.month
        days_in_month = calendar.monthrange(y, m)[1]
        nxt = date(y, m, days_in_month) + timedelta(days=1)
        st.session_state.year, st.session_state.month = nxt.year, nxt.month

# カレンダー表示
cal = calendar.Calendar(firstweekday=0)
weeks = calendar.monthcalendar(st.session_state.year, st.session_state.month)
weekday_names = ["月","火","水","木","金","土","日"]
# ヘッダ
cols = st.columns(7)
for i, name in enumerate(weekday_names):
    cols[i].markdown(f"**{name}**")

# 日付ボタン (クリックで選択)
def select_date(d):
    st.session_state.selected_date = d

for week in weeks:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")  # 空セル
            continue
        d = date(st.session_state.year, st.session_state.month, day)
        # 各自の予約をまとめて表示する
        marks = []
        for name, res_map in st.session_state.reservations.items():
            info = res_map.get(d.isoformat())
            if info:
                marks.append(f"{full_to_short.get(name, name)}:{info['type']}")
        mark = f" ({', '.join(marks)})" if marks else ""
        key = f"day_{d.isoformat()}"
        if cols[i].button(f"{day}{mark}", key=key, on_click=select_date, args=(d.isoformat(),)):
            pass

# 選択日用フォーム
if st.session_state.selected_date:
    sel = st.session_state.selected_date
    st.markdown(f"### 選択日: {sel} （申請者: {applicant}）")
    with st.form(key="apply_form"):
        typ = st.radio("休暇種別", ["AM休", "PM休", "全日"])
        comment = st.text_input("コメント（任意）")
        submitted = st.form_submit_button("保存")
        if submitted:
            st.session_state.reservations.setdefault(applicant, {})[sel] = {"type": typ, "comment": comment}
            st.success("保存しました")
            st.session_state.selected_date = None

# 申請一覧表示（簡易）
st.markdown("#### 保存済み申請")
res_for_app = st.session_state.reservations.get(applicant, {})
if res_for_app:
    for d, info in sorted(res_for_app.items()):
        st.write(f"{d} — {info['type']} — {info['comment']}")
else:
    st.write("なし")