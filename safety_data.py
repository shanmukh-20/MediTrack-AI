"""
safety_data.py
Educational drug interaction knowledge base for MediTrack AI.
Demonstration dataset covering common clinically-documented interactions,
biological mechanisms, severity categories, and practical safety advice.
"""

# Structured educational dataset of interactions
INTERACTION_RULES = [
    {
        "pair": {"aspirin", "warfarin"},
        "severity": "Severe",
        "title": "Aspirin + Warfarin (Anticoagulant & Antiplatelet Synergism)",
        "mechanism": "Both medications inhibit hemostasis via distinct biological pathways: Aspirin inhibits platelet cyclooxygenase-1 (COX-1), blocking thromboxane A2 synthesis; Warfarin competitively inhibits Vitamin K epoxide reductase (VKORC1), depleting clotting factors II, VII, IX, and X. Combined use substantially elevates systemic bleeding risk.",
        "management": "Requires strict medical supervision, frequent INR monitoring, and dose adjustment. Alternative analgesic strategies (e.g., paracetamol at monitored doses) are generally preferred."
    },
    {
        "pair": {"aspirin", "ibuprofen"},
        "severity": "Moderate",
        "title": "Aspirin + Ibuprofen (Competitive COX-1 Inhibition & GI Risk)",
        "mechanism": "Ibuprofen reversibly binds to the COX-1 active site, competitively blocking irreversible acetylation by low-dose cardio-protective aspirin. Concurrent use diminishes aspirin's cardioprotective efficacy and increases gastric mucosal irritation and peptic ulcer risk.",
        "management": "Take aspirin at least 30 minutes before ibuprofen, or wait 8 hours after ibuprofen before taking aspirin. Consult a physician."
    },
    {
        "pair": {"paracetamol", "alcohol"},
        "severity": "Severe",
        "title": "Paracetamol (Acetaminophen) + Ethanol (Hepatotoxicity Risk)",
        "mechanism": "Ethanol induces hepatic Cytochrome P450 2E1 (CYP2E1), accelerating the oxidation of paracetamol into N-acetyl-p-benzoquinone imine (NAPQI), a cytotoxic reactive metabolite. When endogenous glutathione is depleted, NAPQI causes hepatocellular necrosis.",
        "management": "Avoid alcohol consumption while taking paracetamol. Do not exceed the maximum daily therapeutic limit (4,000 mg/day; lower in liver-impaired individuals)."
    },
    {
        "pair": {"ciprofloxacin", "calcium carbonate"},
        "severity": "Moderate",
        "title": "Ciprofloxacin + Calcium Carbonate / Antacids (Chelation Chelation)",
        "mechanism": "Divalent and trivalent cations (Ca2+, Mg2+, Al3+, Fe2+) form insoluble chelate complexes with fluoroquinolone antibiotics in the gastrointestinal tract, reducing ciprofloxacin oral bioavailability by up to 90%.",
        "management": "Administer ciprofloxacin at least 2 hours before or 6 hours after taking calcium supplements, antacids, or dairy products."
    },
    {
        "pair": {"lisinopril", "potassium chloride"},
        "severity": "Severe",
        "title": "Lisinopril + Potassium Supplements (Risk of Hyperkalemia)",
        "mechanism": "Lisinopril inhibits Angiotensin Converting Enzyme (ACE), decreasing aldosterone secretion from the adrenal cortex. Lower aldosterone reduces renal potassium excretion in the distal tubules. Exogenous potassium supplementation can lead to life-threatening cardiac arrhythmias.",
        "management": "Serum potassium levels must be routinely monitored. Avoid potassium supplements or salt substitutes unless specifically prescribed by a physician."
    },
    {
        "pair": {"atorvastatin", "clarithromycin"},
        "severity": "Severe",
        "title": "Atorvastatin + Clarithromycin (CYP3A4 Inhibition)",
        "mechanism": "Clarithromycin is a potent inhibitor of hepatic and intestinal Cytochrome P450 3A4 (CYP3A4), the primary enzyme responsible for atorvastatin clearance. Inhibition causes pronounced elevation in serum statin concentrations, increasing the risk of myopathy and rhabdomyolysis.",
        "management": "Temporarily suspend atorvastatin during short antibiotic therapy, or switch to an alternative macrolide/antibiotic with minimal CYP3A4 interaction (e.g., azithromycin)."
    },
    {
        "pair": {"metformin", "alcohol"},
        "severity": "Moderate",
        "title": "Metformin + Alcohol (Lactic Acidosis Risk)",
        "mechanism": "Ethanol metabolism increases the hepatic NADH/NAD+ ratio, inhibiting gluconeogenesis and the conversion of lactate to glucose. In combination with metformin's inhibition of mitochondrial complex I, this potentiates the risk of lactic acidosis and hypoglycemia.",
        "management": "Limit or avoid heavy alcohol consumption while taking metformin. Seek urgent medical care if experiencing weakness, hyperventilation, or severe muscle aches."
    },
    {
        "pair": {"omeprazole", "clopidogrel"},
        "severity": "Moderate",
        "title": "Omeprazole + Clopidogrel (CYP2C19 Bioactivation Inhibition)",
        "mechanism": "Clopidogrel is a prodrug requiring bioactivation by CYP2C19 into its active thiol metabolite. Omeprazole competitively inhibits CYP2C19, decreasing clopidogrel antiplatelet action and raising the risk of ischemic cardiac events.",
        "management": "Consider pantoprazole or an H2-receptor antagonist instead of omeprazole, as pantoprazole displays substantially lower CYP2C19 affinity."
    },
    {
        "pair": {"sertraline", "tramadol"},
        "severity": "Severe",
        "title": "Sertraline + Tramadol (Serotonin Syndrome Risk)",
        "mechanism": "Sertraline inhibits serotonin reuptake (SSRI), while tramadol both stimulates serotonin release and inhibits its reuptake. Concurrent therapy creates excessive 5-HT receptor activation in the central nervous system, risking serotonin syndrome (tremors, hyperthermia, delirium).",
        "management": "Avoid concurrent use or monitor closely for symptoms such as agitation, hyperreflexia, and diaphoresis."
    },
    {
        "pair": {"amoxicillin", "methotrexate"},
        "severity": "Moderate",
        "title": "Amoxicillin + Methotrexate (Decreased Renal Clearance)",
        "mechanism": "Penicillin antibiotics compete with methotrexate for organic anion transporters (OAT1/OAT3) in renal proximal tubules, leading to reduced methotrexate excretion and elevated systemic toxicity (myelosuppression, stomatitis).",
        "management": "Monitor methotrexate blood levels and complete blood counts carefully when penicillins are co-prescribed."
    },
    {
        "pair": {"levothyroxine", "calcium carbonate"},
        "severity": "Moderate",
        "title": "Levothyroxine + Calcium Supplements (Absorption Adsorption)",
        "mechanism": "Calcium salts bind non-specifically to levothyroxine in an acidic gastric environment, forming insoluble complexes that drastically impair thyroid hormone absorption.",
        "management": "Separate the administration of levothyroxine and calcium supplements by at least 4 hours."
    },
    {
        "pair": {"digoxin", "amiodarone"},
        "severity": "Severe",
        "title": "Digoxin + Amiodarone (P-glycoprotein & Clearance Inhibition)",
        "mechanism": "Amiodarone inhibits P-glycoprotein (P-gp / ABCB1) efflux transporters in renal and biliary pathways, reducing digoxin elimination by approximately 50% and doubling serum digoxin concentrations, leading to digitalis toxicity.",
        "management": "Empirically reduce digoxin dose by 30% to 50% upon initiating amiodarone, with close serum digoxin and ECG monitoring."
    }
]

# Aliases and generic synonyms mapping
SYNONYMS = {
    "acetaminophen": "paracetamol",
    "tylenol": "paracetamol",
    "panadol": "paracetamol",
    "crocin": "paracetamol",
    "calpol": "paracetamol",
    "aspirin": "aspirin",
    "ecotrin": "aspirin",
    "disprin": "aspirin",
    "ibuprofen": "ibuprofen",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "brufen": "ibuprofen",
    "warfarin": "warfarin",
    "coumadin": "warfarin",
    "alcohol": "alcohol",
    "ethanol": "alcohol",
    "beer": "alcohol",
    "wine": "alcohol",
    "ciprofloxacin": "ciprofloxacin",
    "cipro": "ciprofloxacin",
    "calcium carbonate": "calcium carbonate",
    "calcium": "calcium carbonate",
    "caltrate": "calcium carbonate",
    "tums": "calcium carbonate",
    "lisinopril": "lisinopril",
    "zestril": "lisinopril",
    "prinivil": "lisinopril",
    "potassium chloride": "potassium chloride",
    "potassium": "potassium chloride",
    "klor-con": "potassium chloride",
    "atorvastatin": "atorvastatin",
    "lipitor": "atorvastatin",
    "clarithromycin": "clarithromycin",
    "biaxin": "clarithromycin",
    "metformin": "metformin",
    "glucophage": "metformin",
    "omeprazole": "omeprazole",
    "prilosec": "omeprazole",
    "clopidogrel": "clopidogrel",
    "plavix": "clopidogrel",
    "sertraline": "sertraline",
    "zoloft": "sertraline",
    "tramadol": "tramadol",
    "ultram": "tramadol",
    "amoxicillin": "amoxicillin",
    "amoxil": "amoxicillin",
    "augmentin": "amoxicillin",
    "methotrexate": "methotrexate",
    "trexall": "methotrexate",
    "levothyroxine": "levothyroxine",
    "synthroid": "levothyroxine",
    "eltroxin": "levothyroxine",
    "digoxin": "digoxin",
    "lanoxin": "digoxin",
    "amiodarone": "amiodarone",
    "cordarone": "amiodarone",
}

def normalize_name(name):
    """Normalize input string to standard generic key."""
    if not name:
        return ""
    clean = name.strip().lower()
    return SYNONYMS.get(clean, clean)


def check_drug_interactions(medication_list):
    """
    Checks pairwise interactions between all provided medicines.
    Returns:
    {
        "checked": [list of strings],
        "interaction_count": int,
        "results": [list of interaction dicts]
    }
    """
    clean_meds = [m.strip() for m in medication_list if m and m.strip()]
    normalized_meds = [(orig, normalize_name(orig)) for orig in clean_meds]

    results = []
    seen_pairs = set()

    for i in range(len(normalized_meds)):
        for j in range(i + 1, len(normalized_meds)):
            orig_a, norm_a = normalized_meds[i]
            orig_b, norm_b = normalized_meds[j]

            pair_key = tuple(sorted([norm_a, norm_b]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            for rule in INTERACTION_RULES:
                if norm_a in rule["pair"] and norm_b in rule["pair"]:
                    results.append({
                        "drug_a": orig_a,
                        "drug_b": orig_b,
                        "severity": rule["severity"],
                        "title": rule["title"],
                        "mechanism": rule["mechanism"],
                        "management": rule["management"]
                    })

    return {
        "checked": clean_meds,
        "interaction_count": len(results),
        "results": results
    }


def get_available_knowledge_drugs():
    """Returns sorted list of commonly checked drugs in the demo dataset."""
    drugs = sorted(list(set(SYNONYMS.keys())))
    return drugs
