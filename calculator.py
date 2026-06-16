# calculator.py

def calculate_media(final_vol_ml, fbs_percent, penstrep_percent,
                    glutamine_mM=None, cytokine_ng_per_ml=None,
                    stock_cytokine_ug_per_ml=None):
    """
    final_vol_ml: total volume in mL
    fbs_percent: e.g., 10 for 10% FBS
    penstrep_percent: e.g., 1 for 1% Pen/Strep
    glutamine_mM: final concentration (e.g., 2 mM) - optional
    cytokine_ng_per_ml: final conc in ng/mL - optional
    stock_cytokine_ug_per_ml: stock concentration - required if cytokine used
    """
    base_medium = final_vol_ml
    results = {}

    # FBS
    if fbs_percent > 0:
        fbs_vol = final_vol_ml * (fbs_percent / 100)
        results['FBS'] = round(fbs_vol, 1)
        base_medium -= fbs_vol

    # Pen/Strep
    if penstrep_percent > 0:
        ps_vol = final_vol_ml * (penstrep_percent / 100)
        results['Pen/Strep'] = round(ps_vol, 1)
        base_medium -= ps_vol

    # Glutamine (assuming 200 mM stock solution, common)
    if glutamine_mM:
        glut_vol = final_vol_ml * (glutamine_mM / 200)  # C1V1 = C2V2
        results['Glutamine (200 mM stock)'] = round(glut_vol, 1)
        base_medium -= glut_vol

    # Cytokine
    if cytokine_ng_per_ml and stock_cytokine_ug_per_ml:
        # Convert stock to ng/µL: 1 µg/mL = 1 ng/µL
        stock_ng_per_ul = stock_cytokine_ug_per_ml  # since 1 µg/mL = 1 ng/µL
        target_ng_per_ml = cytokine_ng_per_ml
        # Volume of stock (µL) to add to final_vol_ml
        cytokine_vol_ul = (target_ng_per_ml * final_vol_ml) / stock_ng_per_ul
        results['Cytokine stock'] = round(cytokine_vol_ul, 1)
        # Convert µL to mL for base medium subtraction
        base_medium -= cytokine_vol_ul / 1000

    results['Base medium (e.g., DMEM)'] = round(base_medium, 1)

    return results