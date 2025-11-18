import math
import pandas as pd
import streamlit as st
import altair as alt

# ---------------------------------------
# 画面設定
# ---------------------------------------
st.set_page_config(page_title="個体群増加モデル（ロジスティック）", layout="wide")

st.markdown(
    "<h3 style='font-size:22px; color:#333;'>個体群の増加モデル（ロジスティック）</h3>",
    unsafe_allow_html=True
)

st.write("左メニューで N₀・r（負の値可）・K・t を直接入力して調整できます。")

st.latex(r"\frac{dN}{dt} = rN\left(1-\frac{N}{K}\right)")
st.latex(r"N_t = \frac{K}{1 + \left(\frac{K-N_0}{N_0}\right)e^{-rt}}")


# ---------------------------------------
# サイドバー：number_input
# ---------------------------------------
st.sidebar.header("パラメータ設定")

N0 = st.sidebar.number_input(
    "N₀（初期個体数）",
    min_value=1,
    max_value=10000,
    value=100,
    step=10
)

r = st.sidebar.number_input(
    "r（内的増殖率・負の値可）",
    min_value=-5.0,
    max_value=5.0,
    value=0.5,
    step=0.01,
    format="%.3f"
)

K = st.sidebar.number_input(
    "K（環境収容力）",
    min_value=1,
    max_value=100000,
    value=500,
    step=50
)

t_max = st.sidebar.number_input(
    "t の最大値（期間）",
    min_value=1,
    max_value=1000,
    value=10,
    step=1
)


# ---------------------------------------
# パラメータの妥当性チェック
# ---------------------------------------
# 1) r < 0 かつ K < N0 の場合：
#    連続ロジスティックの理論解の分母が有限時間で 0 になり、
#    その先で発散・符号反転して「おかしな値」になるため計算を止める
if r < 0 and K < N0:
    st.error(
        "このパラメータの組み合わせ（r < 0 かつ K < N₀）では、"
        "ロジスティック方程式の理論解の分母が有限時間で 0 になり、"
        "個体数が発散してしまいます。\n\n"
        "・r を 0 以上にするか\n"
        "・K を N₀ 以上にする\n\n"
        "のいずれかになるように値を調整してください。"
    )
    st.stop()  # ここで以降の計算・表示を中止

# ---------------------------------------
# 計算：ロジスティックモデル
# ---------------------------------------
t_values = list(range(int(t_max) + 1))
A = (K - N0) / N0

N_values = []
for t in t_values:
    denom = 1.0 + A * math.exp(-r * t)
    # 念のため、分母が 0 または負になりそうな場合は None にしておく（表とグラフで欠損扱い）
    if denom <= 0:
        N_values.append(None)
    else:
        N_values.append(K / denom)

df = pd.DataFrame({"t": t_values, "N": N_values})


# ---------------------------------------
# テーブル表示
# ---------------------------------------
st.subheader("計算結果（テーブル）")
st.dataframe(df.style.format({"N": "{:.3f}"}), use_container_width=True)


# ---------------------------------------
# グラフ（Altair）
# ---------------------------------------
st.subheader("時間とともに変化する個体数 N のグラフ")

# None が含まれている場合は Altair がその点を自動的に飛ばして描画します
chart = (
    alt.Chart(df)
    .mark_line()
    .encode(
        x=alt.X("t:Q", title="t（時間）"),
        y=alt.Y("N:Q", title="N（個体数）"),
    )
    .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)
