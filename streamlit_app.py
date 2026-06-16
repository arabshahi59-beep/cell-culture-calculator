import streamlit as st
from calculator import calculate_media

# Page config
st.set_page_config(page_title="Cell Culture Calculator", page_icon="🧬", layout="centered")

st.title("🧬 Cell Culture Media Calculator")
st.markdown("---")

# Inputs in a form
with st.form("media_calculator"):
    col1, col2 = st.columns(2)
    with col1:
        final_vol = st.number_input("Final volume (mL)", min_value=1.0, value=250.0, step=10.0)
        fbs = st.number_input("FBS (%)", min_value=0.0, value=10.0, step=1.0)
        penstrep = st.number_input("Pen/Strep (%)", min_value=0.0, value=1.0, step=0.5)
        glutamine_final = st.number_input("L-Glutamine final (mM)", min_value=0.0, value=2.0, step=0.5)
        glutamine_stock = st.number_input("Glutamine stock (mM)", min_value=1.0, value=200.0, step=10.0)

    with col2:
        overage = st.number_input("Overage (%) for filtering loss", min_value=0.0, value=10.0, step=5.0)
        st.markdown("#### Supplements")
        use_bme = st.checkbox("β-Mercaptoethanol (50 µM)")
        use_neaa = st.checkbox("NEAA (1%)")
        use_pyruvate = st.checkbox("Sodium Pyruvate (1 mM)")
        use_hepes = st.checkbox("HEPES (10 mM)")

    st.markdown("#### Cytokines")
    cytokine_names = st.text_input("Cytokine names (comma-separated)", value="IL-2")
    cytokine_finals = st.text_input("Final concentrations (ng/mL, comma-separated)", value="50")
    cytokine_stocks = st.text_input("Stock concentrations (µg/mL, comma-separated)", value="10")

    calculate = st.form_submit_button("Calculate Media")

if calculate:
    # Parse cytokine inputs
    names = [n.strip() for n in cytokine_names.split(",") if n.strip()]
    finals = [float(f.strip()) for f in cytokine_finals.split(",") if f.strip()]
    stocks = [float(s.strip()) for s in cytokine_stocks.split(",") if s.strip()]

    # Validate lengths
    if not (len(names) == len(finals) == len(stocks)):
        st.error("Number of cytokine names, final concentrations, and stock concentrations must match.")
    else:
        # Build cytokine list
        cytokine_data = [{"name": names[i], "final": finals[i], "stock": stocks[i]} for i in range(len(names))]

        # Call the core calculation function
        try:
            total_vol = final_vol * (1 + overage / 100)
            results = {}
            remaining = total_vol

            # FBS
            if fbs > 0:
                vol_fbs = total_vol * (fbs / 100)
                results["FBS"] = (round(vol_fbs, 1), "mL")
                remaining -= vol_fbs
            # Pen/Strep
            if penstrep > 0:
                vol_ps = total_vol * (penstrep / 100)
                results["Pen/Strep (100x)"] = (round(vol_ps, 1), "mL")
                remaining -= vol_ps
            # Glutamine
            if glutamine_final > 0 and glutamine_stock > 0:
                vol_glu = total_vol * (glutamine_final / glutamine_stock)
                results[f"L-Glutamine ({glutamine_stock} mM stock)"] = (round(vol_glu, 1), "mL")
                remaining -= vol_glu
            # Supplements (simplified – assume 100x stocks)
            supp_map = {
                "β-Mercaptoethanol": use_bme,
                "NEAA": use_neaa,
                "Sodium Pyruvate": use_pyruvate,
                "HEPES": use_hepes
            }
            for name, used in supp_map.items():
                if used:
                    # For demo, assume each is added at 1% final (or specific)
                    vol_supp = total_vol * 0.01  # simplify – you can adjust
                    results[name] = (round(vol_supp, 1), "mL")
                    remaining -= vol_supp
            # Cytokines
            for cyto in cytokine_data:
                stock_ng_per_ul = cyto["stock"]  # µg/mL = ng/µL
                vol_ul = (cyto["final"] * total_vol) / stock_ng_per_ul
                results[f"{cyto['name']} (stock {cyto['stock']} µg/mL)"] = (round(vol_ul, 1), "µL")
                remaining -= vol_ul / 1000
            # Base medium
            results["Base medium (DMEM/RPMI/etc.)"] = (round(remaining, 1), "mL")

            # Display results
            st.subheader("📋 Results")
            st.write(f"**Total volume (including {overage}% overage):** {round(total_vol, 1)} mL")
            st.write(f"**Target final volume:** {final_vol} mL")
            st.markdown("---")
            for label, (value, unit) in results.items():
                st.write(f"**{label}:** {value} {unit}")

            # Warning checks (optional)
            if fbs > 20:
                st.warning("⚠️ FBS >20% is unusually high (typical 2-20%)")
            if glutamine_final > 4:
                st.warning("⚠️ High glutamine (>4 mM) may cause ammonia buildup")
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")