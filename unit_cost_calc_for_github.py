import streamlit as st
import pandas as pd
from io import BytesIO

# 입력값: 전체 조정 변수
with st.expander("> 조정변수설정", expanded=False):
    st.sidebar.header("조정 변수")

def get_global_inputs():
    labor_cost_per_person = st.sidebar.number_input("인당 인건비 (원)", value=100000)
    total_personnel = st.sidebar.number_input("총 인원 수", value=5)
    general_admin_rate = st.sidebar.number_input("일반관리비 (%)", value=5.0)
    interest_rate = st.sidebar.number_input("금리 (%)", value=3.0)
    profit_margin = st.sidebar.number_input("이윤 (%)", value=10.0)
    return labor_cost_per_person, total_personnel, general_admin_rate, interest_rate, profit_margin

# 단가 산출 계산 함수
def calculate_unit_cost(
    pack_unit, box_quantity, purchase_price, yield_rate,
    film_price, box_price,
    labor_cost_per_person, total_personnel,
    general_admin_rate, interest_rate, profit_margin
):
    raw_material_cost = round(purchase_price / (yield_rate / 100))
    packaging_cost = round(film_price + box_price / box_quantity)
    total_labor_cost = labor_cost_per_person * total_personnel
    labor_cost_per_kg = round(total_labor_cost / 1000)
    indirect_cost = round((raw_material_cost + packaging_cost + labor_cost_per_kg) * (
        (general_admin_rate + interest_rate) / 100
    ))
    total_cost = raw_material_cost + packaging_cost + labor_cost_per_kg + indirect_cost
    final_unit_cost = round(total_cost * (1 + profit_margin / 100))
    return final_unit_cost, {
        "원재료비": raw_material_cost,
        "포장재비": packaging_cost,
        "인건비": labor_cost_per_kg,
        "간접비": indirect_cost,
        "이윤 적용 전 원가": total_cost
    }

# Streamlit UI
st.title("단가 산출 프로그램 (프로토타입 v2)")

# 전체 조정 변수
(
    labor_cost_per_person, total_personnel,
    general_admin_rate, interest_rate, profit_margin
) = get_global_inputs()

# 품목 리스트 저장용 변수
if "product_list" not in st.session_state:
    st.session_state["product_list"] = []

st.subheader("📦 품목별 입력")
product_name = st.text_input("품목명")
pack_unit = st.number_input("팩 단위 (g)", value=500)
box_quantity = st.number_input("박스 입수량 (팩)", value=10)
purchase_price = st.number_input("입고가 (원/kg)", value=10000)
yield_rate = st.number_input("수율 (%)", value=80.0)
film_price = st.number_input("필름 가격 (원/EA)", value=114)
box_price = st.number_input("박스 가격 (원/EA)", value=930)

if st.button("단가 계산하기"):
    final_cost, details = calculate_unit_cost(
        pack_unit, box_quantity, purchase_price, yield_rate,
        film_price, box_price,
        labor_cost_per_person, total_personnel,
        general_admin_rate, interest_rate, profit_margin
    )

    st.subheader(f"✅ 최종 단가: {final_cost:,} 원/kg")
    st.write("### 구성 항목")
    for name, val in details.items():
        st.write(f"- {name}: {val:,} 원")

    # 품목 정보 저장
    st.session_state.product_list.append({
        "품목명": product_name,
        "최종단가": final_cost,
        **details
    })

# 저장된 품목 리스트 테이블로 표시 및 엑셀 다운로드
st.subheader("📋 계산된 품목 리스트")

# 새로고침 버튼
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🔄 리스트 초기화"):
        st.session_state.product_list = []
        st.success("품목 리스트가 초기화되었습니다.")

if st.session_state.product_list:
    df = pd.DataFrame(st.session_state.product_list)
    st.dataframe(df)

    def convert_df_to_csv(df):
        df = df.copy()
        for col in df.select_dtypes(include='number').columns:
            df[col] = df[col].round(0).astype(int)
        return df.to_csv(index=False).encode('utf-8-sig')

    csv_data = convert_df_to_csv(df)
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv_data,
        file_name="단가산출_리스트.csv",
        mime="text/csv"
    )
