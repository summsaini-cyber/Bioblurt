import streamlit as st
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
import time

# PWA support
st.markdown("""
    <link rel="manifest" href="manifest.json">
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('sw.js');
        }
    </script>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="BioBlurt — AQA Biology Active Recall",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============ CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0a0a0a; }

    div[data-testid="stHorizontalBlock"] { align-items: center !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        display: flex; flex-direction: column; justify-content: center;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div { width: 100%; }

    .new-text { color: #666; font-size: 12px; display: block; text-align: center; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .rag-status { display: block; text-align: center; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .rag-red { color: #ff5555; } .rag-amber { color: #ffaa33; } .rag-green { color: #55ff88; }

    .rank-badge {
        display: inline-block; padding: 3px 10px; border-radius: 10px;
        font-weight: 700; font-size: 10px; letter-spacing: 0.5px; text-transform: uppercase;
    }
    .rank-beginner { background-color: #3a1a1a; color: #ff5555; border: 1px solid #ff5555; }
    .rank-developing { background-color: #3a2a1a; color: #ffaa33; border: 1px solid #ffaa33; }
    .rank-proficient { background-color: #1a3a1a; color: #55ff88; border: 1px solid #55ff88; }
    .rank-advanced { background-color: #1a2a3a; color: #5599ff; border: 1px solid #5599ff; }
    .rank-master { background-color: #2a1a3a; color: #cc66ff; border: 1px solid #cc66ff; }

    .stTextArea textarea {
        font-size: 16px; border-radius: 14px; border: 2px solid #222;
        background-color: #111; color: #eee !important; padding: 20px; line-height: 1.7;
    }
    .stTextArea textarea:focus { border-color: #4CAF50; box-shadow: 0 0 0 4px rgba(76,175,80,0.08); }
    .stTextArea textarea::placeholder { color: #555; }

    .stButton button { border-radius: 12px; font-weight: 600; transition: all 0.2s ease; }
    .stButton button:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,0.4); }
    .stButton > button[kind="primary"] { background-color: #4CAF50; border: none; }
    .stButton > button[kind="primary"]:hover { background-color: #45a049; }

    .score-display { font-size: 64px; font-weight: 800; text-align: center; margin: 28px 0; letter-spacing: -3px; }

    .dashboard-card {
        background: linear-gradient(145deg, #141414, #1a1a1a);
        border: 1px solid #222; border-radius: 16px; padding: 20px; margin-bottom: 12px;
    }
    .dashboard-stat { font-size: 32px; font-weight: 800; color: #fff; }
    .dashboard-label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; }

    .weak-topic-card {
        background: linear-gradient(145deg, #1a1111, #221111);
        border: 1px solid #331111; border-radius: 12px;
        padding: 14px 18px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s;
    }
    .weak-topic-card:hover { border-color: #ff5555; transform: translateX(4px); }

    .topic-card-main {
        background: linear-gradient(145deg, #141414, #1a1a1a);
        border: 1px solid #222; border-radius: 14px;
        padding: 18px 20px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s;
    }
    .topic-card-main:hover { border-color: #4CAF50; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(76,175,80,0.1); }

    .progress-bar-bg { background: #222; border-radius: 8px; height: 8px; overflow: hidden; }
    .progress-bar-fill { height: 100%; border-radius: 8px; transition: width 0.5s ease; }

    .tracker-item {
        background: #111; border: 1px solid #222; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 10px;
    }
    .tracker-item:hover { border-color: #333; }

    .tracker-covered { border-left: 4px solid #4CAF50; }
    .tracker-uncovered { border-left: 4px solid #444; }

    h1, h2, h3 { color: #fff !important; }
    p, li { color: #ccc !important; }
</style>
""", unsafe_allow_html=True)

# ============ DATA ============
DATA_FILE = "bioblurt_progress.json"

def safe_load_progress():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except:
        pass
    return {}

def safe_save_progress(progress):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2)
        return True
    except:
        return False

# ============ COMPLETE AQA SPEC ============
AQA_TOPICS = {
    "3.1 Biological molecules": {
        "3.1.1 Monomers and polymers": [
            "Monomers are the smaller units from which larger molecules (polymers) are made. Monosaccharides, amino acids and nucleotides are examples of monomers.",
            "Polymers are molecules made from a large number of monomers joined together. They are formed by condensation reactions and broken down by hydrolysis.",
            "A condensation reaction joins two molecules together with the formation of a chemical bond and involves the elimination of a molecule of water.",
            "A hydrolysis reaction breaks a chemical bond between two molecules and involves the use of a water molecule. It is essentially the reverse of condensation."
        ],
        "3.1.2 Carbohydrates": [
            "Monosaccharides are the monomers from which larger carbohydrates are made. Glucose, galactose and fructose are common monosaccharides.",
            "A condensation reaction between two monosaccharides forms a glycosidic bond. This is a covalent bond formed between two monosaccharide units.",
            "Maltose is a disaccharide formed by condensation of two glucose molecules. It is found in germinating seeds.",
            "Sucrose is a disaccharide formed by condensation of a glucose molecule and a fructose molecule. It is the transport sugar in plants.",
            "Lactose is a disaccharide formed by condensation of a glucose molecule and a galactose molecule. It is the sugar found in milk.",
            "Glucose has two isomers: alpha-glucose and beta-glucose. The difference lies in the position of the hydroxyl group on carbon-1.",
            "Polysaccharides are formed by the condensation of many glucose units. They serve as storage or structural molecules.",
            "Glycogen and starch are formed by the condensation of alpha-glucose. Glycogen is the storage polysaccharide in animals; starch is the storage polysaccharide in plants.",
            "Cellulose is formed by the condensation of beta-glucose. It is the main structural component of plant cell walls.",
            "The basic structure of glycogen: highly branched polymer of alpha-glucose with 1-4 and 1-6 glycosidic bonds. It is compact and insoluble, making it ideal for storage in liver and muscle cells.",
            "The basic structure of starch: mixture of amylose (unbranched, helical, 1-4 bonds) and amylopectin (branched, 1-4 and 1-6 bonds). It is insoluble and does not affect water potential.",
            "The basic structure of cellulose: straight chains of beta-glucose joined by 1-4 glycosidic bonds. Parallel chains are cross-linked by hydrogen bonds to form microfibrils, providing strength.",
            "The relationship of structure to function of glycogen: highly branched structure means glucose can be rapidly hydrolysed and released for respiration. Compact and insoluble so does not affect osmosis.",
            "The relationship of structure to function of starch: insoluble and compact so does not affect water potential. Can be hydrolysed to glucose for respiration when needed.",
            "The relationship of structure to function of cellulose: straight chains with hydrogen bonds form strong microfibrils. Provides rigidity and strength to plant cell walls, preventing bursting under osmotic pressure.",
            "Benedict's test for reducing sugars: add Benedict's reagent and heat. A positive result is a colour change from blue to green, yellow, orange or brick-red precipitate.",
            "Benedict's test for non-reducing sugars: first hydrolyse with dilute acid, neutralise, then perform Benedict's test. A positive result confirms non-reducing sugars like sucrose.",
            "Iodine potassium iodide test for starch: add iodine in potassium iodide solution. A positive result is a colour change from yellow-brown to blue-black."
        ],
        "3.1.3 Lipids": [
            "Triglycerides and phospholipids are two groups of lipid. Both are esters formed from glycerol and fatty acids.",
            "Triglycerides are formed by the condensation of one molecule of glycerol and three molecules of fatty acid. They are the main energy storage molecules in animals and plants.",
            "A condensation reaction between glycerol and a fatty acid forms an ester bond. Three ester bonds form in a triglyceride.",
            "The R-group of a fatty acid may be saturated or unsaturated. Saturated fatty acids have no double bonds between carbon atoms; unsaturated fatty acids have one or more double bonds.",
            "In phospholipids, one of the fatty acids of a triglyceride is substituted by a phosphate-containing group. This makes the molecule amphipathic — it has a hydrophilic phosphate head and hydrophobic fatty acid tails.",
            "The different properties of triglycerides and phospholipids related to their different structures. Triglycerides are entirely hydrophobic and used for energy storage. Phospholipids form bilayers because their phosphate heads interact with water while their fatty acid tails avoid water.",
            "The emulsion test for lipids: shake the sample with ethanol, then pour into water. A positive result is a cloudy white emulsion."
        ],
        "3.1.4 Proteins": [
            "Amino acids are the monomers from which proteins are made. There are twenty amino acids that are common in all organisms.",
            "The general structure of an amino acid: a central carbon atom bonded to an NH2 amine group, a COOH carboxyl group, a hydrogen atom, and an R side chain. The twenty amino acids differ only in their side group.",
            "A condensation reaction between two amino acids forms a peptide bond. A dipeptide is formed from two amino acids; a polypeptide is formed from many amino acids.",
            "A functional protein may contain one or more polypeptides. The sequence and number of amino acids determines the protein's structure and function.",
            "The role of hydrogen bonds in the structure of proteins: hydrogen bonds form between the partially positive hydrogen of the N-H group and the partially negative oxygen of the C=O group. These stabilise the secondary structure (alpha-helix and beta-pleated sheet).",
            "The role of ionic bonds in the structure of proteins: ionic bonds form between positively and negatively charged R-groups. These help stabilise the tertiary structure.",
            "The role of disulfide bridges in the structure of proteins: strong covalent bonds form between sulfur atoms in cysteine residues. These significantly stabilise the tertiary structure.",
            "The relationship between primary, secondary, tertiary and quaternary structure, and protein function. The primary structure (sequence of amino acids) determines how the protein folds into secondary and tertiary structures, which in turn determine its specific function.",
            "The biuret test for proteins: add sodium hydroxide solution, then copper sulfate solution. A positive result is a colour change from blue to lilac or purple, indicating peptide bonds are present."
        ],
        "3.1.5 Nucleic acids": [
            "Deoxyribonucleic acid (DNA) and ribonucleic acid (RNA) are important information-carrying molecules. In all living cells, DNA holds genetic information and RNA transfers genetic information from DNA to the ribosomes.",
            "Ribosomes are formed from RNA and proteins. They are the site of protein synthesis.",
            "Both DNA and RNA are polymers of nucleotides. Each nucleotide is formed from a pentose sugar, a nitrogen-containing organic base and a phosphate group.",
            "The components of a DNA nucleotide are deoxyribose, a phosphate group and one of the organic bases adenine, cytosine, guanine or thymine.",
            "The components of an RNA nucleotide are ribose, a phosphate group and one of the organic bases adenine, cytosine, guanine or uracil.",
            "A condensation reaction between two nucleotides forms a phosphodiester bond. This creates the sugar-phosphate backbone of DNA and RNA.",
            "A DNA molecule is a double helix with two polynucleotide chains held together by hydrogen bonds between specific complementary base pairs. Adenine pairs with thymine (two hydrogen bonds); guanine pairs with cytosine (three hydrogen bonds).",
            "An RNA molecule is a relatively short polynucleotide chain. It is usually single-stranded and contains uracil instead of thymine.",
            "The semi-conservative replication of DNA ensures genetic continuity between generations of cells. Each new DNA molecule contains one original strand and one newly synthesised strand.",
            "The role of DNA helicase in unwinding DNA and breaking its hydrogen bonds. Helicase separates the two strands by breaking the hydrogen bonds between complementary bases, exposing the nucleotide bases.",
            "The attraction of new DNA nucleotides to exposed bases on template strands and base pairing. Free DNA nucleotides are attracted to their complementary bases on the template strands.",
            "The role of DNA polymerase in the condensation reaction that joins adjacent nucleotides. DNA polymerase catalyses the formation of phosphodiester bonds between the new nucleotides, synthesising the new strand in the 5' to 3' direction."
        ],
        "3.1.6 ATP": [
            "A single molecule of adenosine triphosphate (ATP) is a nucleotide derivative and is formed from a molecule of ribose, a molecule of adenine and three phosphate groups.",
            "Hydrolysis of ATP to adenosine diphosphate (ADP) and an inorganic phosphate group (Pi) is catalysed by the enzyme ATP hydrolase.",
            "The hydrolysis of ATP can be coupled to energy-requiring reactions within cells. When ATP is hydrolysed, the energy released drives endergonic reactions such as muscle contraction, active transport and synthesis of macromolecules.",
            "The inorganic phosphate released during the hydrolysis of ATP can be used to phosphorylate other compounds, often making them more reactive. Phosphorylation activates substrate molecules, lowering their activation energy.",
            "ATP is resynthesised by the condensation of ADP and Pi. This is an endergonic reaction that requires energy input.",
            "The resynthesis of ATP is catalysed by the enzyme ATP synthase during photosynthesis, or during respiration. In photosynthesis, energy comes from light; in respiration, energy comes from the oxidation of glucose."
        ],
        "3.1.7 Water": [
            "Water is a major component of cells. It makes up approximately 70-80% of the mass of most cells.",
            "Water is a metabolite in many metabolic reactions, including condensation and hydrolysis reactions. It is both a reactant and a product in many biochemical pathways.",
            "Water is an important solvent in which metabolic reactions occur. Its polarity allows it to dissolve ions and polar molecules, facilitating transport and chemical reactions.",
            "Water has a relatively high heat capacity, buffering changes in temperature. This means large amounts of energy are required to raise its temperature, helping organisms maintain stable internal temperatures.",
            "Water has a relatively large latent heat of vaporisation, providing a cooling effect with little loss of water through evaporation. This is important in thermoregulation, such as sweating in mammals.",
            "Water has strong cohesion between water molecules; this supports columns of water in the tube-like transport cells of plants and produces surface tension where water meets air. Cohesion is due to hydrogen bonding between water molecules."
        ],
        "3.1.8 Inorganic ions": [
            "Inorganic ions occur in solution in the cytoplasm and body fluids of organisms, some in high concentrations and others in very low concentrations.",
            "Each type of ion has a specific role, depending on its properties.",
            "Hydrogen ions and pH: hydrogen ions determine the pH of solutions. Enzymes have optimum pH values; deviations can cause denaturation.",
            "Iron ions as a component of haemoglobin: iron is found in the haem group of haemoglobin and is essential for oxygen binding and transport.",
            "Sodium ions in the co-transport of glucose and amino acids: sodium ions create electrochemical gradients that drive the active transport of glucose and amino acids into cells.",
            "Phosphate ions as components of DNA and of ATP: phosphate groups form the backbone of DNA and RNA, and the high-energy bonds in ATP."
        ]
    },
    "3.2 Cells": {
        "3.2.1 Cell structure": [
            "The structure and function of the nucleus: contains chromatin (DNA and histones), nucleolus (produces ribosomal RNA), and is surrounded by a nuclear envelope with nuclear pores that control entry and exit of materials.",
            "The structure and function of mitochondria: double-membraned organelles with cristae (folded inner membrane) and matrix. Site of aerobic respiration and ATP synthesis via oxidative phosphorylation.",
            "The structure and function of chloroplasts: double-membraned organelles containing thylakoids (stacked into grana) and stroma. Site of photosynthesis.",
            "The structure and function of the Golgi apparatus: stack of flattened membrane-bound sacs (cisternae). Modifies, packages and sorts proteins for secretion or delivery to other organelles.",
            "The structure and function of rough endoplasmic reticulum: membrane system with ribosomes attached. Synthesises proteins that are exported from the cell or inserted into membranes.",
            "The structure and function of smooth endoplasmic reticulum: membrane system without ribosomes. Synthesises lipids and steroids, and stores and releases calcium ions.",
            "The structure and function of ribosomes: small organelles made of RNA and protein. Site of protein synthesis (translation). Found free in cytoplasm or attached to rough ER.",
            "The structure and function of lysosomes: membrane-bound vesicles containing hydrolytic enzymes. Break down waste material, foreign material and worn-out organelles.",
            "The structure and function of vacuoles: membrane-bound sacs containing cell sap. In plant cells, the large central vacuole maintains turgor pressure and stores ions and metabolites.",
            "The structure and function of the cell wall: in plants, made of cellulose microfibrils in a matrix of pectin and hemicellulose. Provides structural support and protection.",
            "The structure and function of the plasma membrane: phospholipid bilayer with embedded proteins, cholesterol and glycolipids. Controls entry and exit of substances.",
            "The structure of prokaryotic cells: cell wall (containing peptidoglycan/murein), plasma membrane, capsule (slime layer for protection), circular DNA (nucleoid), plasmids (small circular DNA), flagella (for movement), pili (for attachment and conjugation).",
            "The differences between prokaryotic and eukaryotic cells: prokaryotes have no nucleus, no membrane-bound organelles, smaller ribosomes (70S), circular DNA, and cell walls containing peptidoglycan. Eukaryotes have a nucleus, membrane-bound organelles, larger ribosomes (80S), linear DNA associated with histones, and cell walls containing cellulose (plants) or chitin (fungi)."
        ],
        "3.2.2 All cells arise from other cells": [
            "The cell cycle: interphase (G1, S, G2), prophase, metaphase, anaphase, telophase and cytokinesis.",
            "Interphase: the cell grows (G1), replicates its DNA (S), and prepares for division (G2). During S phase, each chromosome is replicated to form two identical sister chromatids joined at the centromere.",
            "Prophase: chromatin condenses into visible chromosomes. The nuclear envelope breaks down. Centrioles move to opposite poles and spindle fibres begin to form.",
            "Metaphase: chromosomes line up along the equator of the cell. Spindle fibres from opposite poles attach to the centromeres of each chromosome.",
            "Anaphase: centromeres divide and sister chromatids are pulled apart to opposite poles by the shortening of spindle fibres.",
            "Telophase: chromatids reach the poles and uncoil. Nuclear envelopes reform around each set of chromosomes. Spindle fibres break down.",
            "Cytokinesis: the cytoplasm divides. In animal cells, a cleavage furrow forms. In plant cells, a cell plate forms.",
            "Mitosis as cell division that gives rise to genetically identical cells in which the chromosome number is maintained. Mitosis produces two daughter cells with the same number of chromosomes as the parent cell.",
            "The role of meiosis in producing cells with a haploid number of chromosomes. Meiosis reduces the chromosome number by half, producing four genetically different haploid cells.",
            "The events of meiosis including homologous chromosomes pairing (synapsis), crossing over (exchange of genetic material between non-sister chromatids), separation of homologous chromosomes (in meiosis I), and separation of sister chromatids (in meiosis II)."
        ],
        "3.2.3 Transport across cell membranes": [
            "The structure of cell surface membranes as a fluid mosaic model: a phospholipid bilayer with proteins, cholesterol and carbohydrates embedded or attached.",
            "The role of the phospholipid bilayer: hydrophilic phosphate heads face outward towards water; hydrophobic fatty acid tails face inward, creating a barrier to water-soluble substances.",
            "The role of proteins in membrane structure: channel proteins form pores for ions; carrier proteins bind specific molecules and change shape to transport them; receptor proteins bind hormones and neurotransmitters.",
            "The role of cholesterol in membrane structure: fits between phospholipid molecules, restricting their movement at high temperatures and preventing crystallisation at low temperatures, thus maintaining membrane fluidity.",
            "The role of glycolipids in membrane structure: carbohydrate chains attached to lipids on the outer surface. Involved in cell recognition and cell signalling.",
            "Diffusion as the net movement of particles from a region where they are in higher concentration to a region where their concentration is lower. It is a passive process requiring no metabolic energy.",
            "Facilitated diffusion involving channel proteins and carrier proteins: channel proteins form hydrophilic pores allowing ions to pass through; carrier proteins bind specific molecules and change shape to transport them across. Both are passive processes.",
            "Osmosis as the diffusion of water from a region of higher water potential to a region of lower water potential across a partially permeable membrane. Water potential is the pressure created by water molecules.",
            "Active transport as the movement of particles against a concentration gradient using energy from ATP. Requires carrier proteins and is essential for accumulating ions and molecules inside cells.",
            "The role of carrier proteins and co-transport in active transport: carrier proteins bind specific solutes and use ATP to pump them against their gradient. Co-transport uses the movement of one substance down its gradient to power the movement of another substance against its gradient.",
            "Exocytosis and endocytosis as bulk transport mechanisms. Exocytosis: vesicles fuse with the plasma membrane, releasing contents outside the cell. Endocytosis: the plasma membrane invaginates to form a vesicle, bringing materials into the cell. Both require ATP."
        ],
        "3.2.4 Cell recognition and the immune system": [
            "Phagocytosis by phagocytes including neutrophils and macrophages: pathogens are engulfed by phagocytes, enclosed in a phagosome, which fuses with a lysosome. Hydrolytic enzymes digest the pathogen. Residual body ejects waste.",
            "The role of T-helper cells in activating B cells: T-helper cells recognise antigen-presenting cells (APCs) via MHC class II molecules. Activated T-helper cells release cytokines that stimulate B cells to divide and differentiate.",
            "B cell activation and clonal selection: when a B cell encounters its specific antigen, it is activated by T-helper cells. The B cell undergoes clonal expansion, producing many identical plasma cells and memory B cells.",
            "The role of plasma cells in antibody production: plasma cells are differentiated B cells that secrete large quantities of specific antibodies into the blood and lymph.",
            "The structure of antibodies: Y-shaped proteins with two identical heavy polypeptide chains and two identical light polypeptide chains. Each has variable regions that bind to specific antigens and constant regions that determine the antibody class.",
            "The primary immune response: slower response on first exposure to a pathogen. Takes time for B cells to proliferate and differentiate into plasma cells. Lower antibody concentration.",
            "The secondary immune response: faster and stronger response on re-exposure to the same pathogen. Memory B cells are already present and rapidly differentiate into plasma cells, producing a much higher antibody concentration.",
            "The use of monoclonal antibodies in diagnosis and treatment: produced by hybridoma cells (fused B cells and myeloma cells). Used in pregnancy tests, ELISA assays, and targeted cancer therapies."
        ]
    },
    "3.3 Organisms exchange substances": {
        "3.3.1 Surface area to volume ratio": [
            "The relationship between the size of an organism and its surface area to volume ratio. As an organism increases in size, its surface area to volume ratio decreases.",
            "Changes to body shape and the development of systems in larger organisms as adaptations that facilitate exchange. Flattened body shapes, specialised exchange surfaces (gills, lungs, intestines), and mass transport systems (circulatory systems) compensate for the reduced surface area to volume ratio."
        ],
        "3.3.2 Gas exchange": [
            "Gas exchange across the body surface of a single-celled organism: occurs by diffusion directly across the cell surface membrane. The large surface area to volume ratio allows sufficient gas exchange without specialised structures.",
            "Gas exchange in the tracheal system of insects: air enters through spiracles and moves through a network of tracheae and tracheoles. Oxygen diffuses directly to tissues; carbon dioxide diffuses out. No respiratory pigment is needed.",
            "Gas exchange across the gills of fish including the counter-current principle: water flows over the gills in the opposite direction to blood flow in the capillaries. This maintains a concentration gradient along the entire length of the gill filament, maximising oxygen uptake efficiency.",
            "Gas exchange by the leaves of dicotyledonous plants including the role of stomata: carbon dioxide enters and oxygen exits through stomata (pores mostly in the lower epidermis). Guard cells control stomatal opening and closing. Gas exchange occurs in the air spaces of the spongy mesophyll.",
            "The structure of the human gas exchange system including alveoli, bronchioles, bronchi, trachea and lungs. The trachea splits into two bronchi, which divide into bronchioles, which end in clusters of alveoli.",
            "The essential features of alveolar epithelium as a gas exchange surface: large surface area (approximately 70m squared in humans), thin walls (one cell thick), good blood supply (dense capillary network), and moist surface (dissolves gases).",
            "Ventilation and gas exchange in the lungs: breathing ventilates the lungs, maintaining steep concentration gradients for oxygen and carbon dioxide between alveolar air and blood.",
            "The mechanism of breathing including the role of the diaphragm and intercostal muscles. Inhalation: external intercostal muscles contract, ribcage moves up and out; diaphragm contracts and flattens; volume increases, pressure decreases, air enters. Exhalation: internal intercostal muscles contract, ribcage moves down and in; diaphragm relaxes and domes up; volume decreases, pressure increases, air exits."
        ],
        "3.3.3 Digestion and absorption": [
            "The digestion of carbohydrates by amylases and membrane-bound disaccharidases: salivary and pancreatic amylases hydrolyse starch to maltose. Membrane-bound disaccharidases (maltase, sucrase, lactase) on epithelial cells hydrolyse disaccharides to monosaccharides.",
            "The digestion of lipids by lipase including the action of bile salts: lipase from the pancreas hydrolyses triglycerides to fatty acids and glycerol. Bile salts emulsify lipids, increasing surface area for lipase action.",
            "The digestion of proteins by endopeptidases, exopeptidases and membrane-bound dipeptidases: endopeptidases (pepsin, trypsin, chymotrypsin) hydrolyse peptide bonds within the polypeptide chain. Exopeptidases remove terminal amino acids. Dipeptidases on epithelial membranes hydrolyse dipeptides to amino acids.",
            "Co-transport mechanisms for the absorption of amino acids and monosaccharides: sodium ions are actively transported out of epithelial cells by the sodium-potassium pump. This creates a sodium concentration gradient. Sodium ions enter the cell down their gradient via co-transport proteins, bringing glucose or amino acids with them.",
            "The role of micelles in the absorption of lipids: bile salts form micelles around lipid digestion products (fatty acids and monoglycerides). Micelles transport lipids to the epithelial membrane where they diffuse into the cell. Inside the cell, lipids are reassembled into triglycerides and packaged into chylomicrons."
        ],
        "3.3.4 Mass transport": [
            "The role of haemoglobin and red blood cells in the transport of oxygen: haemoglobin is a globular protein with four polypeptide chains, each with a haem group containing iron. Each haem group binds one oxygen molecule. Red blood cells are biconcave discs with no nucleus, maximising surface area for oxygen diffusion and space for haemoglobin.",
            "The loading, transport and unloading of oxygen in relation to the oxyhaemoglobin dissociation curve: at high partial pressures of oxygen (in the lungs), haemoglobin loads oxygen to form oxyhaemoglobin. At low partial pressures (in tissues), oxygen is unloaded. The S-shaped curve reflects cooperative binding.",
            "The cooperative nature of oxygen binding to haemoglobin: binding of the first oxygen molecule increases the affinity of haemoglobin for subsequent oxygen molecules. This produces the sigmoid shape of the dissociation curve.",
            "The Bohr effect as the effect of carbon dioxide concentration on the dissociation of oxyhaemoglobin: increased carbon dioxide lowers blood pH (more hydrogen ions), which reduces haemoglobin's affinity for oxygen. This shifts the dissociation curve to the right, promoting oxygen unloading in metabolically active tissues.",
            "The general pattern of blood circulation in a mammal: double circulatory system. Pulmonary circulation (right ventricle to lungs to left atrium) and systemic circulation (left ventricle to body to right atrium).",
            "The gross structure of the human heart: four chambers (right atrium, right ventricle, left atrium, left ventricle). Valves (tricuspid, bicuspid/mitral, semilunar) prevent backflow. Septum separates oxygenated and deoxygenated blood.",
            "Pressure and volume changes during the cardiac cycle: atrial systole (atria contract, ventricles fill); ventricular systole (ventricles contract, atrioventricular valves close, semilunar valves open, blood ejected); diastole (all chambers relax, semilunar valves close, atrioventricular valves open, ventricles fill).",
            "The structure of arteries, arterioles and veins in relation to their function. Arteries: thick muscular walls, elastic tissue, narrow lumen — withstand high pressure, maintain blood flow. Arterioles: muscular walls that constrict/dilate to control blood flow. Veins: thin walls, wide lumen, valves — low pressure return.",
            "The structure of capillaries and the importance of capillary beds: walls one cell thick, narrow lumen (single file of red blood cells), numerous and highly branched. This creates a large surface area and short diffusion distance for exchange.",
            "The formation of tissue fluid and its return to the circulatory system: at the arterial end of capillaries, hydrostatic pressure forces fluid out (filtration). At the venous end, osmotic pressure draws fluid back in (reabsorption). Excess tissue fluid drains into lymphatic vessels as lymph.",
            "Xylem as tissue that transports water in plants: xylem vessels are dead, hollow tubes with lignified walls and no end walls. They form continuous columns from roots to leaves.",
            "The cohesion-tension theory of water transport in xylem: transpiration pull creates tension (negative pressure) in the xylem. Cohesion between water molecules (hydrogen bonding) and adhesion between water and xylem walls allows water to be pulled up the plant as a continuous column.",
            "Phloem as tissue that transports organic substances in plants: composed of sieve tube elements and companion cells. Sieve tube elements are living cells with perforated end walls (sieve plates) but lack nuclei. Companion cells provide metabolic support.",
            "The mass flow hypothesis for the mechanism of translocation in plants: sucrose is actively loaded into phloem at source (e.g. leaves), lowering water potential. Water enters by osmosis, creating high hydrostatic pressure. At sink (e.g. roots, fruits), sucrose is removed, water exits, pressure drops. This pressure gradient drives mass flow of sap."
        ]
    },
    "3.4 Genetic information": {
        "3.4.1 DNA, genes and chromosomes": [
            "A gene as a sequence of nucleotides that codes for a polypeptide or functional RNA. Genes are the units of heredity.",
            "The locus of a gene on a chromosome: the specific position of a gene on a particular chromosome.",
            "Alleles as variants of a gene: different versions of the same gene that arise by mutation and occupy the same locus on homologous chromosomes.",
            "The structure of chromosomes including centromere and telomeres. The centromere is the region where sister chromatids are joined. Telomeres are repetitive DNA sequences at the ends of chromosomes that protect them from degradation."
        ],
        "3.4.2 DNA and protein synthesis": [
            "Transcription as the production of mRNA from a DNA template: RNA polymerase binds to the promoter region of a gene and synthesises a complementary mRNA strand using the DNA template strand.",
            "The role of RNA polymerase in transcription: RNA polymerase unwinds the DNA double helix, reads the template strand in the 3' to 5' direction, and synthesises mRNA in the 5' to 3' direction.",
            "The splicing of pre-mRNA to remove introns and join exons: pre-mRNA contains both coding sequences (exons) and non-coding sequences (introns). Spliceosomes remove introns and join exons together to form mature mRNA.",
            "Translation as the role of ribosomes, mRNA, tRNA and codons: ribosomes read the mRNA sequence in groups of three nucleotides (codons). Each codon specifies a particular amino acid. tRNA molecules bring the correct amino acids to the ribosome, matching their anticodons to the mRNA codons.",
            "The role of start and stop codons in translation: the start codon (AUG) codes for methionine and signals the beginning of translation. Stop codons (UAA, UAG, UGA) do not code for amino acids and signal the termination of translation."
        ],
        "3.4.3 Genetic diversity": [
            "Meiosis and genetic variation through crossing over and independent assortment: crossing over during prophase I exchanges genetic material between homologous chromosomes. Independent assortment during metaphase I randomly orientates homologous chromosome pairs, creating new combinations of maternal and paternal chromosomes.",
            "Mutations as a source of genetic variation: mutations are sudden changes in the amount or arrangement of genetic material. They create new alleles.",
            "The types of mutation including substitution, deletion, insertion, inversion and duplication. Substitution: one base replaced by another. Deletion: one or more bases removed. Insertion: one or more bases added. Inversion: sequence reversed. Duplication: sequence repeated."
        ],
        "3.4.4 Genetic diversity and adaptation": [
            "Natural selection as a mechanism for evolution: individuals with advantageous alleles are more likely to survive and reproduce, passing those alleles to the next generation. Over time, allele frequencies change.",
            "Species as groups of organisms with similar morphology and physiology that can interbreed to produce fertile offspring.",
            "Reproductive isolation as a barrier to gene flow: mechanisms that prevent interbreeding between species, maintaining separate gene pools. Includes pre-zygotic (behavioural, temporal, mechanical, gametic) and post-zygotic (hybrid inviability, hybrid sterility) barriers."
        ],
        "3.4.5 Species and taxonomy": [
            "The binomial system of naming species: each species is given a two-part Latin name (genus and species). For example, Homo sapiens.",
            "Courtship behaviour as part of reproductive isolation: specific behaviours that allow individuals to recognise members of their own species and coordinate mating. Prevents wasted reproductive effort and hybridisation.",
            "Evidence for relatedness between organisms: DNA hybridisation, comparison of amino acid sequences in proteins, comparison of DNA base sequences, and morphological/embryological similarities."
        ],
        "3.4.6 Investigating diversity": [
            "The index of diversity formula: d = N(N-1) / Σn(n-1), where N is the total number of organisms and n is the number of individuals of each species. Higher values indicate greater diversity.",
            "Genetic diversity within and between populations: genetic diversity within populations is measured by the proportion of heterozygotes or the number of alleles per gene locus. Genetic diversity between populations can be assessed by comparing allele frequencies."
        ]
    },
    "3.5 Energy transfers": {
        "3.5.1 Photosynthesis": [
            "The light-dependent reaction including photoionisation of chlorophyll, photolysis of water, electron transport chain, and production of ATP and reduced NADP: occurs in thylakoid membranes. Light energy excites electrons in chlorophyll. Water is split (photolysis) to replace electrons, releasing oxygen and protons. Electrons pass along carriers, releasing energy used to pump protons and synthesise ATP. NADP is reduced.",
            "The light-independent reaction including the Calvin cycle, carbon fixation, reduction of glycerate-3-phosphate, and regeneration of ribulose bisphosphate: occurs in the stroma. Carbon dioxide is fixed by RuBisCO to RuBP, forming an unstable 6C compound that splits into two glycerate-3-phosphate (GP). GP is reduced to triose phosphate (TP) using ATP and reduced NADP. Most TP is used to regenerate RuBP; some forms glucose.",
            "The factors affecting the rate of photosynthesis: light intensity (affects light-dependent reactions), carbon dioxide concentration (affects Calvin cycle), and temperature (affects enzyme activity). Limiting factors determine the maximum rate."
        ],
        "3.5.2 Respiration": [
            "Glycolysis including phosphorylation of glucose, lysis into triose phosphate, and oxidation to pyruvate: occurs in cytoplasm. Glucose is phosphorylated (using 2 ATP) to hexose bisphosphate. Split into two triose phosphate molecules. Oxidised to pyruvate, producing 2 ATP and 2 reduced NAD per glucose.",
            "The link reaction including decarboxylation and dehydrogenation of pyruvate to form acetylcoenzyme A: occurs in mitochondrial matrix. Pyruvate loses CO2 (decarboxylation) and hydrogen (dehydrogenation). Remaining 2C acetyl group combines with coenzyme A to form acetylcoenzyme A. Produces reduced NAD.",
            "The Krebs cycle including decarboxylation and dehydrogenation, substrate-level phosphorylation, and formation of reduced coenzymes: occurs in mitochondrial matrix. Acetylcoenzyme A combines with oxaloacetate (4C) to form citrate (6C). Two decarboxylations produce CO2. Four dehydrogenations produce reduced NAD and reduced FAD. One substrate-level phosphorylation produces ATP.",
            "The electron transport chain and oxidative phosphorylation: occurs on inner mitochondrial membrane (cristae). Reduced NAD and reduced FAD donate electrons to the chain. Electrons pass through carriers, releasing energy used to pump protons into the intermembrane space. Protons flow back through ATP synthase, driving ATP synthesis. Oxygen is the final electron acceptor, forming water.",
            "Anaerobic respiration in animals and yeast: in animals, pyruvate is reduced to lactate by reduced NAD, regenerating NAD for glycolysis. In yeast, pyruvate is decarboxylated to ethanal, which is reduced to ethanol by reduced NAD, regenerating NAD. Both produce only 2 ATP per glucose."
        ],
        "3.5.3 Energy and ecosystems": [
            "Gross primary production (GPP) and net primary production (NPP): GPP is the total energy fixed by photosynthesis. NPP = GPP - respiratory losses. NPP represents energy available to consumers.",
            "The efficiency of energy transfer between trophic levels: typically only about 10% of energy is transferred from one trophic level to the next. Losses occur through respiration, heat, excretion, and uneaten parts.",
            "The recycling of nitrogen and phosphorus in ecosystems: decomposers break down organic matter, releasing inorganic ions. Nitrifying bacteria convert ammonium to nitrites and nitrates. Nitrogen-fixing bacteria convert atmospheric nitrogen to ammonia."
        ],
        "3.5.4 Nutrient cycling": [
            "The role of microorganisms in decomposition: saprobiontic microorganisms (bacteria and fungi) secrete extracellular enzymes to digest dead organic matter, absorbing the products. They release inorganic ions through ammonification and mineralisation.",
            "The nitrogen cycle including nitrogen fixation, nitrification, denitrification and ammonification: nitrogen fixation converts atmospheric N2 to ammonia. Nitrification converts ammonia to nitrites then nitrates. Denitrification converts nitrates back to N2 gas. Ammonification converts organic nitrogen to ammonia.",
            "The phosphorus cycle: phosphorus is released by weathering of rocks. Absorbed by plants as phosphate ions. Passed through food chains. Returned to soil by decomposition and excretion. No atmospheric component."
        ]
    },
    "3.6 Organisms respond": {
        "3.6.1 Stimuli and responses": [
            "Survival and response including taxes, kineses and tropisms. Taxes: directional movement towards (positive) or away from (negative) a stimulus. Kineses: non-directional movement, rate depends on stimulus intensity. Tropisms: growth responses in plants.",
            "The role of IAA as an auxin in phototropism and gravitropism: IAA (indoleacetic acid) is produced in the shoot tip and transported down the shoot. In phototropism, IAA accumulates on the shaded side, promoting cell elongation and bending towards light. In gravitropism, IAA accumulates on the lower side of roots, inhibiting cell elongation and causing downward growth."
        ],
        "3.6.2 Nervous coordination": [
            "The structure and function of the mammalian nervous system: consists of the central nervous system (brain and spinal cord) and peripheral nervous system (sensory and motor neurones). Sensory neurones carry impulses to CNS; motor neurones carry impulses from CNS to effectors.",
            "The structure and function of a myelinated motor neurone: cell body in CNS, long axon with myelin sheath (formed by Schwann cells), nodes of Ranvier. Myelination insulates and increases speed of conduction via saltatory conduction.",
            "The generation and transmission of action potentials: resting potential (-70mV) maintained by sodium-potassium pump. Stimulus causes depolarisation; if threshold reached, voltage-gated sodium channels open, rapid influx of Na+ causes action potential (+40mV). Repolarisation: Na+ channels close, K+ channels open, K+ efflux restores negative potential. Hyperpolarisation then return to resting potential.",
            "Saltatory conduction: action potentials jump from one node of Ranvier to the next in myelinated neurones. This is faster than continuous conduction because only the nodes need to depolarise.",
            "The structure and function of synapses including neurotransmitters: synaptic knob contains vesicles of neurotransmitter (e.g. acetylcholine). Action potential arrives, Ca2+ channels open, vesicles fuse with presynaptic membrane, neurotransmitter released into synaptic cleft. Binds to receptors on postsynaptic membrane, causing depolarisation (excitatory) or hyperpolarisation (inhibitory). Acetylcholinesterase breaks down neurotransmitter to prevent continuous stimulation."
        ],
        "3.6.3 Muscles": [
            "The structure of skeletal muscle including myofibrils, sarcomeres, actin and myosin filaments: skeletal muscle fibres contain myofibrils. Each myofibril has repeating sarcomeres (Z-line to Z-line). Thin filaments are actin; thick filaments are myosin. Myosin has ATPase heads that bind to actin.",
            "The sliding filament mechanism of muscle contraction: action potential stimulates sarcoplasmic reticulum to release Ca2+. Ca2+ binds to troponin, moving tropomyosin and exposing myosin-binding sites on actin. Myosin heads bind, pull actin filaments toward the centre of the sarcomere (power stroke), then detach and reattach further along. Sarcomere shortens; H-zone and I-band narrow; A-band stays same width.",
            "The role of ATP and calcium ions in muscle contraction: ATP binds to myosin heads, causing detachment from actin. ATP hydrolysis re-energises myosin head. Ca2+ released from sarcoplasmic reticulum binds troponin, initiating contraction. Ca2+ is actively transported back into SR for relaxation."
        ],
        "3.6.4 Homeostasis": [
            "The principles of homeostasis including negative feedback: homeostasis is the maintenance of a stable internal environment. Negative feedback detects deviations from the norm and triggers responses that reverse the deviation, returning the system to its set point.",
            "The control of blood glucose concentration including the role of insulin and glucagon: beta cells in pancreatic islets of Langerhans detect high blood glucose and secrete insulin. Insulin increases glucose uptake by cells, increases glycogenesis (glucose to glycogen) in liver and muscle, and increases glycolysis. Alpha cells detect low blood glucose and secrete glucagon. Glucagon increases glycogenolysis (glycogen to glucose) and gluconeogenesis in the liver.",
            "The control of blood water potential including the role of ADH and osmoreceptors: osmoreceptors in the hypothalamus detect changes in blood water potential. When water potential decreases (more concentrated), ADH is released from the posterior pituitary. ADH increases water permeability of collecting duct walls by inserting aquaporins into cell membranes. More water is reabsorbed, producing concentrated urine. When water potential increases, less ADH is released, producing dilute urine."
        ]
    },
    "3.7 Genetics, populations, evolution": {
        "3.7.1 Inheritance": [
            "Genetic crosses and pedigree diagrams: monohybrid and dihybrid crosses predict offspring ratios. Pedigree diagrams trace inheritance patterns through generations, identifying carriers and affected individuals.",
            "The chi-squared test: statistical test to determine whether observed results differ significantly from expected ratios. Calculate chi-squared value, compare to critical value at appropriate degrees of freedom and significance level (usually p=0.05).",
            "Epistasis and lethal alleles: epistasis occurs when one gene masks the expression of another. Lethal alleles cause death when homozygous, altering expected phenotypic ratios.",
            "Sex linkage and codominance: sex-linked genes are located on sex chromosomes (usually X). Males (XY) express all alleles on their single X. Codominance occurs when both alleles are expressed in the heterozygote (e.g. ABO blood groups)."
        ],
        "3.7.2 Populations": [
            "The Hardy-Weinberg principle and equation: p + q = 1 and p squared + 2pq + q squared = 1, where p and q are allele frequencies. The principle states that allele frequencies remain constant in a large, randomly mating population with no mutation, selection, migration or genetic drift.",
            "Selection pressures and directional, stabilising and disruptive selection: directional selection favours one extreme phenotype. Stabilising selection favours the intermediate phenotype, reducing variation. Disruptive selection favours both extremes, increasing variation."
        ],
        "3.7.3 Evolution": [
            "Speciation including allopatric and sympatric speciation: allopatric speciation occurs when populations are geographically isolated and diverge genetically. Sympatric speciation occurs without geographic isolation, often through polyploidy or ecological/behavioural isolation.",
            "Genetic drift and the bottleneck effect: genetic drift is random change in allele frequencies, especially significant in small populations. The bottleneck effect occurs when a population is drastically reduced, losing genetic diversity.",
            "The founder effect: occurs when a small group colonises a new area. The new population has reduced genetic diversity and may have different allele frequencies from the original population."
        ],
        "3.7.4 Ecosystems": [
            "Succession including primary and secondary succession: primary succession begins on bare rock with pioneer species (e.g. lichens). Soil develops, allowing larger plants to colonise, increasing biodiversity until a climax community forms. Secondary succession occurs on previously colonised land after disturbance (e.g. fire), starting from soil with seeds and organic matter.",
            "The conservation of habitats and species: involves maintaining biodiversity, protecting endangered species, preserving habitats, and managing ecosystems sustainably. Methods include captive breeding, habitat corridors, seed banks, and legal protection."
        ]
    },
    "3.8 The control of gene expression": {
        "3.8.1 Mutations and gene expression": [
            "The types of gene mutation including substitution, deletion and insertion: substitution replaces one base with another (may be silent, missense or nonsense). Deletion removes one or more bases, causing frameshift. Insertion adds one or more bases, causing frameshift.",
            "The effect of mutations on protein structure and function: mutations can alter the primary structure of proteins, changing folding and function. Silent mutations have no effect; missense changes one amino acid; nonsense creates a premature stop codon, producing a truncated protein.",
            "Oncogenes and tumour suppressor genes: proto-oncogenes stimulate cell division. Mutated versions (oncogenes) cause excessive cell division. Tumour suppressor genes normally inhibit cell division or promote apoptosis. Mutations in these genes remove the 'brakes' on cell division, leading to cancer."
        ],
        "3.8.2 Regulation of gene expression": [
            "Transcription factors and gene expression: transcription factors bind to DNA promoter or enhancer regions, activating or repressing transcription. They control which genes are expressed in different cell types.",
            "Oestrogen and the regulation of gene expression: oestrogen is a steroid hormone that diffuses through the plasma membrane and binds to intracellular receptors. The hormone-receptor complex binds to DNA, activating transcription of target genes.",
            "SiRNA and gene silencing: small interfering RNA molecules bind to complementary mRNA sequences, marking them for degradation by the RNA-induced silencing complex (RISC). This prevents translation and reduces gene expression."
        ],
        "3.8.3 Using genome projects": [
            "Gene sequencing and genome sequencing: DNA sequencing determines the order of nucleotides in a DNA fragment. Genome sequencing determines the complete DNA sequence of an organism. The Human Genome Project sequenced the entire human genome.",
            "Bioinformatics and understanding of gene function: bioinformatics uses computer databases and algorithms to analyse DNA and protein sequences. Comparisons between species reveal conserved sequences and gene function."
        ],
        "3.8.4 Gene technologies": [
            "Recombinant DNA technology including restriction endonucleases, ligases and plasmids: restriction endonucleases cut DNA at specific recognition sequences, producing sticky or blunt ends. DNA ligase joins DNA fragments. Plasmids are used as vectors to carry foreign DNA into host cells.",
            "In vivo and in vitro gene cloning: in vivo cloning uses host organisms (e.g. bacteria) to replicate DNA. In vitro cloning uses PCR to amplify DNA without living cells.",
            "Genetic fingerprinting and PCR: PCR (polymerase chain reaction) amplifies specific DNA sequences using primers, DNA polymerase, and thermal cycling. Genetic fingerprinting uses variable number tandem repeats (VNTRs) or short tandem repeats (STRs) to produce unique DNA profiles for identification."
        ]
    }
}


# ============ SCORING ENGINE ============
STOP_WORDS = {
    'the', 'and', 'are', 'from', 'that', 'with', 'for', 'can', 'its', 'has',
    'have', 'this', 'into', 'been', 'they', 'their', 'them', 'than', 'then',
    'when', 'where', 'which', 'while', 'during', 'between', 'through', 'within',
    'under', 'over', 'such', 'each', 'both', 'all', 'any', 'some', 'many',
    'most', 'more', 'less', 'very', 'also', 'only', 'just', 'but', 'not',
    'however', 'therefore', 'because', 'since', 'although', 'though', 'unless',
    'whether', 'either', 'neither', 'yet', 'so', 'as', 'at', 'by', 'in', 'of',
    'on', 'to', 'up', 'via', 'per', 'a', 'an', 'is', 'it', 'be', 'or', 'if',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'must', 'shall', 'was', 'were', 'had', 'having', 'being', 'made', 'used',
    'using', 'form', 'forms', 'formed', 'role', 'roles', 'function', 'functions',
    'structure', 'structures', 'process', 'processes', 'including', 'involves',
    'involving', 'called', 'known', 'found', 'present', 'produced', 'produces',
    'produce', 'give', 'gives', 'given', 'take', 'takes', 'taken', 'make',
    'makes', 'use', 'uses', 'one', 'two', 'three', 'first', 'second', 'third',
    'other', 'another', 'same', 'different', 'similar', 'various', 'certain',
    'specific', 'particular', 'general', 'main', 'major', 'important',
    'essential', 'necessary', 'required', 'needed', 'able', 'due', 'across',
    'along', 'around', 'against', 'towards', 'away', 'down', 'off', 'out',
    'upon', 'without', 'about', 'above', 'after', 'again', 'against', 'ago',
    'before', 'behind', 'below', 'beside', 'besides', 'beyond', 'despite',
    'except', 'inside', 'instead', 'into', 'like', 'near', 'onto', 'outside',
    'past', 'since', 'throughout', 'till', 'toward', 'underneath', 'until',
    'unto', 'upon', 'versus', 'via', 'within', 'worth'
}

def extract_keywords(text):
    words = text.lower().split()
    keywords = []
    for word in words:
        clean = ''.join(c for c in word if c.isalnum())
        if len(clean) >= 4 and clean not in STOP_WORDS:
            keywords.append(clean)
    return keywords

def calculate_score(user_text, spec_points):
    if not user_text or not user_text.strip():
        return 0.0, []
    user_keywords = extract_keywords(user_text)
    if not user_keywords:
        return 0.0, []
    matched_points = []
    for point in spec_points:
        point_keywords = extract_keywords(point)
        if not point_keywords:
            continue
        matched_count = 0
        total_weight = 0
        for pk in point_keywords:
            total_weight += 1
            best = 0
            for uk in user_keywords:
                if pk == uk:
                    best = 1.0
                    break
                elif pk in uk and len(pk) >= 6:
                    best = max(best, 0.5)
                else:
                    ratio = SequenceMatcher(None, pk, uk).ratio()
                    if ratio > 0.88:
                        best = max(best, ratio * 0.6)
            if best >= 0.45:
                matched_count += best
        similarity = matched_count / total_weight if total_weight > 0 else 0
        if similarity >= 0.50:
            matched_points.append(point)
    score = (len(matched_points) / len(spec_points) * 100) if spec_points else 0
    return round(min(score, 100), 1), matched_points

# ============ RANKING & RAG ============
def get_rank(percentage):
    if percentage < 25:
        return "Beginner", "rank-beginner"
    elif percentage < 45:
        return "Developing", "rank-developing"
    elif percentage < 65:
        return "Proficient", "rank-proficient"
    elif percentage < 85:
        return "Advanced", "rank-advanced"
    else:
        return "Master", "rank-master"

def get_rag_status(score, manual_rag=None):
    if manual_rag:
        colors = {"Red": "rag-red", "Amber": "rag-amber", "Green": "rag-green"}
        return manual_rag, colors.get(manual_rag, "rag-red")
    if score < 40:
        return "Red", "rag-red"
    elif score < 65:
        return "Amber", "rag-amber"
    else:
        return "Green", "rag-green"

# ============ SPEC TRACKER HELPERS ============
def get_tracker_key(topic, subtopic, spec_point):
    """Generate a unique key for a spec point in the tracker."""
    safe_point = spec_point[:50].replace(" ", "_").replace("'", "")
    return f"tracker|{topic}|{subtopic}|{safe_point}"

def get_tracker_data(progress, topic, subtopic):
    """Get tracker data for a specific subtopic."""
    tracker = progress.get("tracker", {})
    key_prefix = f"{topic}|{subtopic}"
    result = {}
    for k, v in tracker.items():
        if k.startswith(key_prefix):
            result[k] = v
    return result

def get_spec_tracker_stats(progress):
    """Get overall spec tracker statistics."""
    tracker = progress.get("tracker", {})
    total_points = 0
    covered = 0
    red = amber = green = 0

    for topic_name, subtopics in AQA_TOPICS.items():
        for sub_name, points in subtopics.items():
            for point in points:
                total_points += 1
                key = f"{topic_name}|{sub_name}|{point[:50].replace(' ', '_').replace(chr(39), '')}"
                if key in tracker:
                    covered += 1
                    rag = tracker[key].get("rag", "Red")
                    if rag == "Red": red += 1
                    elif rag == "Amber": amber += 1
                    else: green += 1

    return {
        "total": total_points,
        "covered": covered,
        "coverage_pct": round(covered / total_points * 100, 1) if total_points else 0,
        "red": red,
        "amber": amber,
        "green": green
    }

# ============ DASHBOARD STATS ============
def get_dashboard_stats(progress):
    total_subtopics = sum(len(subs) for subs in AQA_TOPICS.values())
    attempted = 0
    total_score = 0
    red_count = amber_count = green_count = 0
    topic_stats = {}

    for topic_name, subtopics in AQA_TOPICS.items():
        topic_scores = []
        topic_attempted = 0
        for sub in subtopics:
            key = f"{topic_name}|{sub}"
            if key in progress:
                attempted += 1
                score = progress[key].get('best_score', 0)
                total_score += score
                topic_scores.append(score)
                topic_attempted += 1
                manual = progress[key].get('manual_rag', None)
                rag = manual or get_rag_status(score)[0]
                if rag == "Red": red_count += 1
                elif rag == "Amber": amber_count += 1
                else: green_count += 1
        if topic_attempted > 0:
            topic_stats[topic_name] = {
                'avg': round(sum(topic_scores)/len(topic_scores), 1),
                'attempted': topic_attempted,
                'total': len(subtopics)
            }

    avg_score = round(total_score / attempted, 1) if attempted > 0 else 0
    completion = round(attempted / total_subtopics * 100, 1) if total_subtopics > 0 else 0
    total_attempts = sum(p.get('attempts', 0) for p in progress.values() if isinstance(p, dict) and 'attempts' in p)
    hours = round(total_attempts * 5 / 60, 1)

    # Spec tracker stats
    tracker_stats = get_spec_tracker_stats(progress)

    return {
        'total_subtopics': total_subtopics,
        'attempted': attempted,
        'completion': completion,
        'avg_score': avg_score,
        'hours': hours,
        'red': red_count,
        'amber': amber_count,
        'green': green_count,
        'topic_stats': topic_stats,
        'tracker': tracker_stats
    }

def get_weak_topics(progress, limit=5):
    weak = []
    for topic_name, subtopics in AQA_TOPICS.items():
        for sub in subtopics:
            key = f"{topic_name}|{sub}"
            if key in progress:
                data = progress[key]
                best = data.get('best_score', 0)
                manual = data.get('manual_rag', None)
                if manual == "Red" or (manual is None and best < 50):
                    weak.append({
                        'key': key,
                        'topic': topic_name,
                        'subtopic': sub,
                        'score': best,
                        'rag': manual or get_rag_status(best)[0],
                        'reason': 'Manual Red' if manual == 'Red' else f'Score {best}%'
                    })
            else:
                weak.append({
                    'key': key,
                    'topic': topic_name,
                    'subtopic': sub,
                    'score': 0,
                    'rag': 'New',
                    'reason': 'Not attempted'
                })
    weak.sort(key=lambda x: (0 if x['rag'] == 'Red' else 1, x['score']))
    return weak[:limit]

# ============ SESSION STATE ============
if 'progress' not in st.session_state:
    st.session_state.progress = safe_load_progress()

if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None

if 'selected_subtopic' not in st.session_state:
    st.session_state.selected_subtopic = None

if 'current_score' not in st.session_state:
    st.session_state.current_score = 0

if 'blurting_start' not in st.session_state:
    st.session_state.blurting_start = None

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "dashboard"  # dashboard, topic, blurt, tracker

# ============ MAIN UI ============
st.title("🧬 BioBlurt")
st.markdown("<p style='text-align: center; color: #888; margin-top: -10px; font-size: 14px;'>Active Recall + Spec Tracker for AQA A-Level Biology</p>", unsafe_allow_html=True)
st.markdown("---")

# Navigation
if st.session_state.selected_subtopic is None:
    if st.session_state.selected_topic is None:
        # ============ DASHBOARD ============
        stats = get_dashboard_stats(st.session_state.progress)

        # Top stats
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='dashboard-card'><div class='dashboard-stat'>{stats['attempted']}/{stats['total_subtopics']}</div><div class='dashboard-label'>Blurts Done</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='dashboard-card'><div class='dashboard-stat'>{stats['avg_score']}%</div><div class='dashboard-label'>Avg Blurt Score</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='dashboard-card'><div class='dashboard-stat'>{stats['hours']}h</div><div class='dashboard-label'>Time Studied</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='dashboard-card'><div class='dashboard-stat'>{stats['tracker']['coverage_pct']}%</div><div class='dashboard-label'>Spec Covered</div></div>", unsafe_allow_html=True)

        # Spec tracker mini-view
        if stats['tracker']['total'] > 0:
            st.markdown("---")
            st.markdown("### 📋 Spec Tracker Overview")
            tcol1, tcol2, tcol3, tcol4 = st.columns(4)
            with tcol1:
                st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#fff;'>{stats['tracker']['covered']}/{stats['tracker']['total']}</span><br/><span style='color:#888;font-size:12px;'>Points Covered</span></div>", unsafe_allow_html=True)
            with tcol2:
                st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#ff5555;'>{stats['tracker']['red']}</span><br/><span style='color:#888;font-size:12px;'>Red</span></div>", unsafe_allow_html=True)
            with tcol3:
                st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#ffaa33;'>{stats['tracker']['amber']}</span><br/><span style='color:#888;font-size:12px;'>Amber</span></div>", unsafe_allow_html=True)
            with tcol4:
                st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#55ff88;'>{stats['tracker']['green']}</span><br/><span style='color:#888;font-size:12px;'>Green</span></div>", unsafe_allow_html=True)

        # Blurt RAG breakdown
        if stats['attempted'] > 0:
            st.markdown("---")
            st.markdown("### 📊 Blurt Performance")
            rag_col1, rag_col2, rag_col3 = st.columns(3)
            with rag_col1:
                st.markdown(f"<div style='text-align:center;'><span style='font-size:28px;font-weight:800;color:#ff5555;'>{stats['red']}</span><br/><span style='color:#888;font-size:12px;'>Red</span></div>", unsafe_allow_html=True)
            with rag_col2:
                st.markdown(f"<div style='text-align:center;'><span style='font-size:28px;font-weight:800;color:#ffaa33;'>{stats['amber']}</span><br/><span style='color:#888;font-size:12px;'>Amber</span></div>", unsafe_allow_html=True)
            with rag_col3:
                st.markdown(f"<div style='text-align:center;'><span style='font-size:28px;font-weight:800;color:#55ff88;'>{stats['green']}</span><br/><span style='color:#888;font-size:12px;'>Green</span></div>", unsafe_allow_html=True)

        # Topic progress
        if stats['topic_stats']:
            st.markdown("---")
            st.markdown("### 📚 Topic Progress")
            for topic_name, tstat in stats['topic_stats'].items():
                pct = round(tstat['attempted'] / tstat['total'] * 100)
                bar_color = '#4CAF50' if pct >= 80 else '#ffaa33' if pct >= 40 else '#ff5555'
                st.markdown(f"<div style='margin-bottom:12px;'><div style='display:flex;justify-content:space-between;margin-bottom:4px;'><span style='color:#ccc;font-size:13px;'>{topic_name}</span><span style='color:#888;font-size:12px;'>{tstat['attempted']}/{tstat['total']} • {tstat['avg']}% avg</span></div><div class='progress-bar-bg'><div class='progress-bar-fill' style='width:{pct}%;background:{bar_color};'></div></div></div>", unsafe_allow_html=True)

        # Weak topics
        weak = get_weak_topics(st.session_state.progress)
        if weak:
            st.markdown("---")
            st.markdown("### 📉 Recommended Review")
            for wt in weak:
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"<div class='weak-topic-card'><b style='color:#fff;font-size:14px;'>{wt['subtopic']}</b><br/><span style='color:#888;font-size:12px;'>{wt['topic']} • {wt['reason']}</span></div>", unsafe_allow_html=True)
                with c2:
                    if st.button("Review", key=f"review_{wt['key']}"):
                        st.session_state.selected_topic = wt['topic']
                        st.session_state.selected_subtopic = wt['subtopic']
                        st.rerun()

        # Topic selection
        st.markdown("---")
        st.markdown("### 🎯 Select a Topic")

        for topic_name, subtopics in AQA_TOPICS.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📚 {topic_name}", key=f"topic_{topic_name}", use_container_width=True):
                    st.session_state.selected_topic = topic_name
                    st.rerun()
            with col2:
                topic_scores = []
                any_manual = None
                for sub in subtopics:
                    key = f"{topic_name}|{sub}"
                    if key in st.session_state.progress:
                        topic_scores.append(st.session_state.progress[key].get('best_score', 0))
                        if st.session_state.progress[key].get('manual_rag'):
                            any_manual = st.session_state.progress[key]['manual_rag']
                if topic_scores:
                    avg = sum(topic_scores) / len(topic_scores)
                    status, css_class = get_rag_status(avg, any_manual)
                    st.markdown(f"<span class='rag-status {css_class}'>{status}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='new-text'>New</span>", unsafe_allow_html=True)
    else:
        # ============ SUBTOPIC SCREEN ============
        st.subheader(f"📚 {st.session_state.selected_topic}")

        if st.button("← Back to Dashboard", key="back_to_topics"):
            st.session_state.selected_topic = None
            st.rerun()

        st.markdown("---")
        st.markdown("**Select a sub-topic:**")

        subtopics = AQA_TOPICS[st.session_state.selected_topic]
        for subtopic_name in subtopics:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button(f"📝 {subtopic_name}", key=f"sub_{subtopic_name}", use_container_width=True):
                    st.session_state.selected_subtopic = subtopic_name
                    st.rerun()
            with col2:
                key = f"{st.session_state.selected_topic}|{subtopic_name}"
                if key in st.session_state.progress:
                    score = st.session_state.progress[key].get('best_score', 0)
                    manual = st.session_state.progress[key].get('manual_rag', None)
                    status, css_class = get_rag_status(score, manual)
                    st.markdown(f"<span class='rag-status {css_class}'>{status}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='new-text'>New</span>", unsafe_allow_html=True)
            with col3:
                key = f"{st.session_state.selected_topic}|{subtopic_name}"
                if key in st.session_state.progress:
                    score = st.session_state.progress[key].get('best_score', 0)
                    rank, rank_class = get_rank(score)
                    st.markdown(f"<div style='text-align: center; padding-top: 2px;'><span class='rank-badge {rank_class}'>{rank}</span></div>", unsafe_allow_html=True)

else:
    # ============ SUBTOPIC ACTIONS SCREEN ============
    topic = st.session_state.selected_topic
    subtopic = st.session_state.selected_subtopic
    spec_points = AQA_TOPICS[topic][subtopic]

    st.subheader(f"📝 {subtopic}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", key="back_to_subtopics"):
            st.session_state.selected_subtopic = None
            st.session_state.current_score = 0
            st.rerun()
    with col2:
        if st.button("🏠 Dashboard", key="go_home"):
            st.session_state.selected_topic = None
            st.session_state.selected_subtopic = None
            st.session_state.current_score = 0
            st.rerun()

    st.markdown("---")

    # Two modes: Blurt or Tracker
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button("🧠 Blurt Mode", use_container_width=True, type="primary" if st.session_state.app_mode != "tracker" else "secondary"):
            st.session_state.app_mode = "blurt"
            st.rerun()
    with mode_col2:
        if st.button("📋 Spec Tracker", use_container_width=True, type="primary" if st.session_state.app_mode == "tracker" else "secondary"):
            st.session_state.app_mode = "tracker"
            st.rerun()

    # ============ BLURT MODE ============
    if st.session_state.app_mode != "tracker":
        # Current status
        progress_key = f"{topic}|{subtopic}"
        if progress_key in st.session_state.progress:
            data = st.session_state.progress[progress_key]
            current_score = data.get('best_score', 0)
            manual_rag = data.get('manual_rag', None)
            status, css_class = get_rag_status(current_score, manual_rag)
            rank, rank_class = get_rank(current_score)
            attempts = data.get('attempts', 0)
            history = data.get('scores_history', [])

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Status:** <span class='{css_class}'>{status}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Best:** {current_score}%")
            with col3:
                st.markdown(f"<span class='rank-badge {rank_class}'>{rank}</span>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"**Attempts:** {attempts}")

            if len(history) > 1:
                st.markdown(f"<p style='color:#888;font-size:12px;'>Score history: {', '.join(str(h) for h in history[-5:])}%</p>", unsafe_allow_html=True)
            st.markdown("---")

        # Blurt input
        st.markdown("### 🧠 Blurt everything you know:")
        st.markdown("<p style='color: #888; font-size: 14px;'>Type everything you remember. Key concepts matter more than perfect sentences.</p>", unsafe_allow_html=True)

        user_blurt = st.text_area("", height=300, placeholder="Start typing your blurt here...", key="blurt_input")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("✅ Submit Blurt", type="primary", use_container_width=True):
                if user_blurt.strip():
                    score, matched = calculate_score(user_blurt, spec_points)
                    st.session_state.current_score = score

                    time_spent = 0
                    if st.session_state.blurting_start:
                        time_spent = round(time.time() - st.session_state.blurting_start)

                    progress_key = f"{topic}|{subtopic}"
                    existing = st.session_state.progress.get(progress_key, {})
                    best_so_far = existing.get('best_score', 0)
                    new_best = max(score, best_so_far)

                    st.session_state.progress[progress_key] = {
                        "best_score": new_best,
                        "last_score": score,
                        "attempts": existing.get("attempts", 0) + 1,
                        "scores_history": existing.get("scores_history", []) + [score],
                        "manual_rag": existing.get("manual_rag", None),
                        "last_attempt": datetime.now().isoformat(),
                        "total_time": existing.get("total_time", 0) + time_spent
                    }
                    safe_save_progress(st.session_state.progress)
                    st.session_state.blurting_start = None
                    st.rerun()
                else:
                    st.error("Please write something before submitting!")

        # Results
        if st.session_state.current_score > 0 or (f"{topic}|{subtopic}" in st.session_state.progress):
            progress_key = f"{topic}|{subtopic}"
            if st.session_state.current_score > 0:
                display_score = st.session_state.current_score
            else:
                display_score = st.session_state.progress[progress_key].get('best_score', 0)

            st.markdown("---")
            st.markdown("### 📊 Results")

            manual_rag = st.session_state.progress.get(progress_key, {}).get('manual_rag', None)
            status, css_class = get_rag_status(display_score, manual_rag)
            rank, rank_class = get_rank(display_score)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='score-display {css_class}'>{display_score}%</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center;'><span class='rank-badge {rank_class}'>{rank}</span></div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**Status:**")
                st.markdown(f"<span class='{css_class}' style='font-size: 24px;'>{status}</span>", unsafe_allow_html=True)

                if display_score < 40:
                    st.markdown("🔴 **Red** — Needs significant revision")
                elif display_score < 65:
                    st.markdown("🟡 **Amber** — Partial understanding, review missed points")
                elif display_score < 85:
                    st.markdown("🟢 **Green** — Strong recall")
                else:
                    st.markdown("🏆 **Master** — Excellent! Maintain with spaced review")

            # Spec breakdown
            st.markdown("---")
            st.markdown("### 📝 Specification Points Check")

            _, matched = calculate_score(user_blurt if user_blurt.strip() else "", spec_points)

            for point in spec_points:
                if point in matched:
                    st.success(f"✅ {point}")
                else:
                    st.error(f"❌ {point}")

            # Manual RAG override
            st.markdown("---")
            st.markdown("### 🎯 Manual RAG Assessment")
            st.markdown("<p style='color: #888; font-size: 13px;'>Override the auto-score if you feel differently.</p>", unsafe_allow_html=True)

            rag_col1, rag_col2, rag_col3, rag_col4 = st.columns(4)
            with rag_col1:
                if st.button("🔴 Red", key="manual_red", use_container_width=True):
                    st.session_state.progress.setdefault(progress_key, {})
                    st.session_state.progress[progress_key]['manual_rag'] = "Red"
                    safe_save_progress(st.session_state.progress)
                    st.rerun()
            with rag_col2:
                if st.button("🟡 Amber", key="manual_amber", use_container_width=True):
                    st.session_state.progress.setdefault(progress_key, {})
                    st.session_state.progress[progress_key]['manual_rag'] = "Amber"
                    safe_save_progress(st.session_state.progress)
                    st.rerun()
            with rag_col3:
                if st.button("🟢 Green", key="manual_green", use_container_width=True):
                    st.session_state.progress.setdefault(progress_key, {})
                    st.session_state.progress[progress_key]['manual_rag'] = "Green"
                    safe_save_progress(st.session_state.progress)
                    st.rerun()
            with rag_col4:
                if st.button("↩️ Auto", key="manual_auto", use_container_width=True):
                    st.session_state.progress.setdefault(progress_key, {})
                    st.session_state.progress[progress_key]['manual_rag'] = None
                    safe_save_progress(st.session_state.progress)
                    st.rerun()

    # ============ SPEC TRACKER MODE ============
    else:
        st.markdown("---")
        st.markdown("### 📋 Specification Point Tracker")
        st.markdown("<p style='color: #888; font-size: 14px;'>Go through each spec point. Tick if covered, set your confidence level, and add notes.</p>", unsafe_allow_html=True)

        # Initialize tracker in progress if not exists
        if "tracker" not in st.session_state.progress:
            st.session_state.progress["tracker"] = {}

        tracker = st.session_state.progress["tracker"]

        # Count stats for this subtopic
        subtopic_covered = 0
        subtopic_red = subtopic_amber = subtopic_green = 0

        for i, point in enumerate(spec_points):
            safe_key = f"{topic}|{subtopic}|{point[:50].replace(' ', '_').replace(chr(39), '')}"
            point_data = tracker.get(safe_key, {"covered": False, "rag": "Red", "notes": ""})

            # Update from form
            form_key = f"tracker_form_{safe_key}"

            with st.container():
                css_class = "tracker-covered" if point_data.get("covered") else "tracker-uncovered"
                st.markdown(f"<div class='tracker-item {css_class}'>", unsafe_allow_html=True)

                c1, c2, c3 = st.columns([0.5, 3, 1.5])
                with c1:
                    covered = st.checkbox("", value=point_data.get("covered", False), key=f"cov_{form_key}")
                with c2:
                    st.markdown(f"<p style='color:#ccc;font-size:14px;margin:0;'>{point}</p>", unsafe_allow_html=True)
                with c3:
                    rag = st.selectbox("", ["Red", "Amber", "Green"], index=["Red", "Amber", "Green"].index(point_data.get("rag", "Red")), key=f"rag_{form_key}", label_visibility="collapsed")

                notes = st.text_input("Notes (optional)", value=point_data.get("notes", ""), key=f"notes_{form_key}", placeholder="Add notes...")

                st.markdown("</div>", unsafe_allow_html=True)

                # Save if changed
                if covered != point_data.get("covered") or rag != point_data.get("rag") or notes != point_data.get("notes"):
                    tracker[safe_key] = {
                        "covered": covered,
                        "rag": rag,
                        "notes": notes,
                        "updated": datetime.now().isoformat()
                    }
                    st.session_state.progress["tracker"] = tracker
                    safe_save_progress(st.session_state.progress)

                if covered:
                    subtopic_covered += 1
                    if rag == "Red": subtopic_red += 1
                    elif rag == "Amber": subtopic_amber += 1
                    else: subtopic_green += 1

        # Subtopic tracker summary
        st.markdown("---")
        st.markdown("### 📊 Tracker Summary")
        total_pts = len(spec_points)
        coverage = round(subtopic_covered / total_pts * 100, 1) if total_pts else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#fff;'>{subtopic_covered}/{total_pts}</span><br/><span style='color:#888;font-size:11px;'>Covered</span></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#fff;'>{coverage}%</span><br/><span style='color:#888;font-size:11px;'>Coverage</span></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#ff5555;'>{subtopic_red}</span><br/><span style='color:#888;font-size:11px;'>Red</span></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#ffaa33;'>{subtopic_amber}</span><br/><span style='color:#888;font-size:11px;'>Amber</span></div>", unsafe_allow_html=True)
        with c5:
            st.markdown(f"<div style='text-align:center;'><span style='font-size:24px;font-weight:800;color:#55ff88;'>{subtopic_green}</span><br/><span style='color:#888;font-size:11px;'>Green</span></div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #555; font-size: 12px;'>BioBlurt v4.1 | AQA Biology A-Level (7402)</p>", unsafe_allow_html=True)
