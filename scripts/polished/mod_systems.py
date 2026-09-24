# Modules 09, 10, 11, 12: Physiological Systems

CIRCULATION_SLIDES = {
    1: {
        "title": "The Circulatory System: Overview & Organization",
        "explanation": """The **cardiovascular system** provides internal bulk convective transport for multicellular life:

### Primary Functions
- **Transport of Respiratory Gases:** Rapid distribution of oxygen ($O_2$) from respiratory surfaces to metabolizing tissues, and removal of carbon dioxide ($CO_2$).
- **Nutrient & Hormone Delivery:** Absorbed nutrients from the gastrointestinal tract and regulatory endocrine signals delivered to target organs.
- **Waste & Thermal Clearance:** Nitrogenous metabolic wastes transported to kidneys; core thermal energy dispersed to the skin."""
    },
    2: {
        "title": "Open vs. Closed Circulatory Systems",
        "explanation": """Animal circulatory architectures evolved into two primary comparative plans:

### Comparative Morphology
- **Open Circulatory System (Arthropods & Mollusks):** Hemolymph is pumped by the heart through open-ended vessels into large body sinuses (**hemocoel**), directly bathing tissues. Operates under low hydrostatic pressure.
- **Closed Circulatory System (Annelids, Cephalopods, Vertebrates):** Blood remains strictly confined within a continuous network of vessels distinct from interstitial fluid. Allows higher blood pressure, rapid flow, and fine-tuned vascular shunting."""
    },
    3: {
        "title": "Single vs. Double Vertebrate Circulation",
        "explanation": """Vertebrate evolution reflects increasing separation between respiratory and systemic circuits:

### Circuit Evolution
- **Single Circulation (Fishes):** Two-chambered heart (one atrium, one ventricle). Blood passes through heart once per complete circuit: heart $\\rightarrow$ gill capillaries $\\rightarrow$ systemic capillaries $\\rightarrow$ heart. Hydrostatic pressure drops significantly after gills.
- **Double Circulation (Amphibians, Reptiles, Birds, Mammals):** Blood passes through the heart twice per complete circuit. Includes a low-pressure **pulmonary circuit** for gas exchange and a high-pressure **systemic circuit** supplying body tissues."""
    },
    4: {
        "title": "Anatomy of the Human Heart: Chambers & Valves",
        "explanation": """The human heart is a muscular four-chambered dual pump operating in unison:

### Anatomical Chambers & Valves
- **Right Atrium & Ventricle:** Receives deoxygenated venous return from the venae cavae and pumps it through the pulmonary trunk to the lungs.
- **Left Atrium & Ventricle:** Receives oxygenated blood via pulmonary veins and ejects it under high pressure into the **aorta** to supply the entire body. The left ventricular myocardium is three times thicker than the right.
- **Atrioventricular (AV) Valves:** Tricuspid (right) and Bicuspid/Mitral (left); anchored by chordae tendineae to prevent backflow into atria during ventricular contraction.
- **Semilunar Valves:** Pulmonary and Aortic valves; prevent regurgitation from arterial trunks during ventricular relaxation."""
    },
    5: {
        "title": "The Cardiac Cycle: Systole & Diastole",
        "explanation": """The rhythmic mechanical pumping of the heart alternates between contraction and relaxation:

### The Two Phases
- **Systole (Contraction):** Ventricular myocytes contract, intraventricular pressure spikes, closing AV valves (first heart sound, 'lub') and forcing semilunar valves open to eject blood into the aorta and pulmonary arteries.
- **Diastole (Relaxation):** Ventricles relax, ventricular pressure falls below arterial pressure, causing semilunar valves to snap shut (second heart sound, 'dub'). AV valves open and blood passively fills the ventricles."""
    },
    6: {
        "title": "Intrinsic Electrical Conduction System of the Heart",
        "explanation": """Myogenic cardiac contractions are initiated and synchronized by specialized autorhythmic pacemaker cells:

### Conduction Pathway
1. **Sinoatrial (SA) Node:** The primary pacemaker located in the right atrium; spontaneously depolarizes at $\\approx 70\\text{ bpm}$.
2. **Atrioventricular (AV) Node:** Introduces a crucial 0.1-second delay allowing atria to fully empty into ventricles before ventricular systole.
3. **Bundle of His & Purkinje Fibers:** Conduct action potentials rapidly down the interventricular septum and upward through ventricular walls, triggering apex-to-base contraction."""
    },
    7: {
        "title": "Arteries, Arterioles & Hydrostatic Blood Pressure",
        "explanation": """Arteries and arterioles transport high-pressure blood away from the ventricles:

### Structural Adaptations
- **Elastic Arteries (e.g., Aorta):** Thick walls rich in elastin fibers; stretch during systole and recoil during diastole (**Windkessel effect**) to maintain continuous laminar flow.
- **Muscular Arterioles:** Ringed by vascular smooth muscle; act as primary **resistance vessels**. Sympathetic tone and local metabolites modulate diameter (vasoconstriction vs vasodilation) to regulate systemic blood pressure and tissue perfusion."""
    },
    8: {
        "title": "Capillary Dynamics & Microvascular Exchange",
        "explanation": """Capillaries represent the functional epicenter where microvascular exchange occurs:

### Microvascular Exchange Mechanics
- **Single-Layer Endothelium:** Thin squamous endothelial walls surrounded by a basal lamina minimize diffusion distance for gases ($O_2, CO_2$), glucose, and amino acids.
- **Starling Forces:** Fluid filtration at the arteriolar end is driven by hydrostatic pressure exceeding oncotic pressure; fluid reabsorption at the venular end occurs as capillary oncotic pressure exceeds hydrostatic pressure."""
    },
    9: {
        "title": "Venules, Veins & Venous Return Mechanisms",
        "explanation": """Veins return low-pressure, deoxygenated blood back to the heart:

### Capacitance Vessels
- **Thin Tunica Media & High Compliance:** Veins hold approximately 60–70% of systemic blood volume at rest.
- **One-Way Venous Valves:** Semilunar flaps in limbs prevent gravitational blood pooling and retrograde flow.
- **Skeletal Muscle & Respiratory Pumps:** Contracting limb muscles compress deep veins; thoracic pressure drop during inhalation pulls blood toward the right atrium."""
    },
    10: {
        "title": "Composition & Physical Properties of Blood",
        "explanation": """Blood is a specialized liquid connective tissue consisting of cellular elements suspended in plasma:

### Fractionation Breakdown
- **Plasma ($\\approx 55\\%$ of volume):** Straw-colored aqueous solution containing water (90%), electrolytes, nutrients, metabolic wastes, and vital plasma proteins.
- **Formed Elements ($\\approx 45\\%$ of volume / Hematocrit):** Red blood cells (erythrocytes), white blood cells (leukocytes), and cellular fragments (platelets)."""
    },
    11: {
        "title": "Plasma Proteins: Albumin, Globulins & Fibrinogen",
        "explanation": """Plasma proteins perform critical osmotic, immune, and hemostatic functions:

### Key Plasma Proteins
- **Albumin ($\\approx 60\\%$ of plasma protein):** Synthesized exclusively by the liver; provides colloid oncotic pressure preventing edema, and transports hydrophobic fatty acids and hormones.
- **Globulins ($\\alpha, \\beta, \\gamma$):** Alpha and beta globulins transport lipids and metal ions; gamma globulins are **immunoglobulins (antibodies)** secreted by plasma cells for humoral immunity.
- **Fibrinogen:** Soluble precursor protein activated into insoluble fibrin during the coagulation cascade."""
    },
    12: {
        "title": "Erythrocytes (RBCs) & Hemoglobin Dynamics",
        "explanation": """Erythrocytes are structurally optimized for high-capacity oxygen transport:

### Morphological & Functional Specialization
- **Biconcave Disc Geometry:** Maximizes surface-area-to-volume ratio and allows elastic deformation through narrow capillaries.
- **Anucleate in Mammals:** Lack nuclei, mitochondria, and ribosomes, devoting entire intracellular space to **hemoglobin**.
- **Hemoglobin Tetramer:** Contains four globin subunits, each housing an iron-containing **heme** moiety capable of reversibly binding one molecule of $O_2$ ($4\\text{ }O_2$ per hemoglobin)."""
    },
    13: {
        "title": "Leukocytes (WBCs): Immune Defense Lines",
        "explanation": """White blood cells protect the body against infectious pathogens and foreign antigens:

### Major Leukocyte Classes
- **Granulocytes:** Neutrophils (first-line phagocytes in acute bacterial infections), Eosinophils (combat parasitic infections and moderate allergic responses), and Basophils (release histamine and heparin).
- **Agranulocytes:** Monocytes (differentiate into tissue macrophages and dendritic cells) and Lymphocytes (B cells for antibody production, T cells for cell-mediated immunity)."""
    },
    14: {
        "title": "Platelets (Thrombocytes) & Hemostasis",
        "explanation": """Platelets are anucleate cytoplasmic fragments shed by giant bone marrow **megakaryocytes**:

### The Three Stages of Hemostasis
1. **Vascular Spasm:** Immediate local vasoconstriction reducing blood loss at the injury site.
2. **Platelet Plug Formation:** Platelets adhere to exposed subendothelial collagen (via von Willebrand factor), become activated, and release ADP and thromboxane $A_2$ to aggregate a temporary plug.
3. **Coagulation Cascade:** Enzymatic clotting cascade activates **prothrombin into thrombin**, which cleaves soluble **fibrinogen into an insoluble fibrin mesh** that traps erythrocytes to seal the vessel."""
    },
    15: {
        "title": "Cardiovascular Pathophysiology: Atherosclerosis & Hypertension",
        "explanation": """Cardiovascular diseases represent the leading cause of global morbidity:

### Clinical Mechanisms
- **Hypertension:** Chronic elevation in systemic arterial pressure ($>130/80\\text{ mmHg}$), increasing cardiac afterload and predisposing to stroke, heart failure, and renal disease.
- **Atherosclerosis:** Progressive inflammatory disease wherein subendothelial LDL oxidation recruits monocytes, forming fatty streaks that advance into fibrous plaques in coronary and carotid arteries."""
    },
    16: {
        "title": "Myocardial Infarction & Ischemic Heart Disease",
        "explanation": """Coronary artery occlusion deprives myocardium of oxygen and nutrients:

### Clinical Course
- **Coronary Thrombosis:** Rupture of an unstable atherosclerotic plaque exposes thrombogenic core, forming an acute occlusive blood clot.
- **Myocardial Infarction ("Heart Attack"):** Irreversible necrosis of cardiac myocytes downstream of the occlusion.
- **Diagnosis:** ST-segment elevation on ECG and elevated serum cardiac biomarkers (cardiac Troponin I and T)."""
    },
    17: {
        "title": "Lymphatic System & Interstitial Fluid Balance",
        "explanation": """The lymphatic system functions as an auxiliary drainage route for the cardiovascular system:

### Lymphatic Dynamics
- **Fluid Return:** Approximately 2–4 liters of excess filtered capillary fluid fails to be reabsorbed each day. Blind-ended lymphatic capillaries collect this **lymph** and return it to the venous system via the subclavian veins.
- **Lymph Nodes:** Encapsulated lymphoid organs that filter lymph and stage immune responses against captured foreign antigens.
- **Edema:** Obstruction of lymphatic vessels leads to severe localized tissue swelling (lymphedema)."""
    },
    18: {
        "title": "Blood Typing: ABO & Rh Blood Group Systems",
        "explanation": """Transfusion compatibility is dictated by genetically encoded cell-surface antigens:

### Blood Antigen Systems
- **ABO System:** Determined by carbohydrate antigens on erythrocyte membranes (Type A has A antigens and anti-B antibodies; Type B has B antigens and anti-A antibodies; Type AB has both antigens and neither antibody, serving as **universal recipient**; Type O has neither antigen and both antibodies, serving as **universal donor**).
- **Rh System:** Presence (Rh+) or absence (Rh-) of the D antigen. Mismatch can cause hemolytic disease of the newborn (erythroblastosis fetalis) in subsequent pregnancies."""
    },
    19: {
        "title": "Cardiovascular Health: Exercise & Preventive Physiology",
        "explanation": """Lifestyle interventions preserve vascular elasticity and cardiac reserve:

### Physiological Benefits of Aerobic Exercise
- **Cardiomyocyte Hypertrophy:** Physiological eccentric hypertrophy increases stroke volume and lowers resting heart rate (athlete's bradycardia).
- **Endothelial Nitric Oxide ($NO$):** Shear stress enhances endothelial nitric oxide synthase (eNOS) activity, promoting basal vasodilation and reducing arterial stiffness.
- **Metabolic Profile:** Elevates cardioprotective HDL, lowers circulating triglycerides, and improves peripheral insulin sensitivity."""
    }
}

DIGESTION_SLIDES = {
    1: {
        "title": "The Digestive System: Energy & Nutrient Assimilation",
        "explanation": """The digestive system converts ingested food into bioavailable nutrients:

### Four Processing Stages
1. **Ingestion:** Taking food into the oral cavity.
2. **Digestion:** Mechanical and enzymatic breakdown of complex polymers into absorbable monomers.
3. **Absorption:** Transport of digested nutrients across the gastrointestinal epithelium into blood and lymph.
4. **Elimination (Defecation):** Expulsion of indigestible residues and metabolic waste."""
    },
    2: {
        "title": "Dietary Adaptations: Herbivores, Carnivores & Omnivores",
        "explanation": """Digestive tracts exhibit striking anatomical adaptations corresponding to diet:

### Comparative Anatomies
- **Herbivores:** Feed exclusively on plant matter; feature long, complex alimentary canals, enlarged **ceca**, and microbial fermentation chambers to digest resistant plant cellulose.
- **Carnivores:** Consume animal protein; possess sharp canine dentition, highly acidic simple stomachs, and shorter gastrointestinal tracts suited for rapid digestion of meat.
- **Omnivores (Humans):** Adaptable intermediate digestive tract equipped to process both plant and animal tissues."""
    },
    3: {
        "title": "Alimentary Canal Architecture & Motility",
        "explanation": """The human digestive tract is a continuous muscular tube extending from mouth to anus:

### Histological Organization
- **Mucosa:** Inner epithelial lining secreting mucus and digestive enzymes, with high surface area for absorption.
- **Submucosa:** Vascularized connective tissue containing the submucosal (Meissner's) nerve plexus.
- **Muscularis Externa:** Circular and longitudinal smooth muscle layers controlled by the myenteric (Auerbach's) plexus.
- **Peristalsis:** Coordinated involuntary wave-like smooth muscle contractions that propel food boluses forward through the gut."""
    },
    4: {
        "title": "Oral Cavity, Salivary Glands & Mastication",
        "explanation": """Mechanical and chemical digestion begin simultaneously in the mouth:

### Oral Processing
- **Mastication:** Teeth mechanically grind and shred food, expanding surface area for enzymatic attack.
- **Salivary Secretion:** Parotid, submandibular, and sublingual glands secrete saliva containing **salivary amylase** (initiates starch digestion into maltose) and **lysozyme** (antimicrobial defense).
- **Bolus Formation:** Tongue mixes masticated food with mucin to form a cohesive, lubricated **food bolus** for swallowing (deglutition)."""
    },
    5: {
        "title": "Pharynx, Epiglottis & Esophageal Transit",
        "explanation": """Deglutition safely routes food into the digestive tract while protecting the airway:

### Reflex Swallowing Mechanics
- **The Epiglottis:** A cartilaginous flap that swings downward to cover the **glottis** (laryngeal opening) during swallowing, preventing pulmonary aspiration.
- **Esophagus:** A muscular conduit transporting the bolus into the abdominal cavity via primary peristaltic waves.
- **Lower Esophageal Sphincter (LES):** A physiological valve that relaxes to allow food passage into the stomach and constricts to prevent acidic gastric reflux (heartburn/GERD)."""
    }
}
