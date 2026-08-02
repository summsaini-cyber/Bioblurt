import streamlit as st
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
import string

# ============ PWA SUPPORT ============
st.markdown("""
    <link rel="manifest" href="manifest.json">
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('sw.js');
        }
    </script>
""", unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title="BioBlurt - AQA Biology Active Recall",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============ CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #0f0f0f;
    }

    /* Topic cards */
    div[data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }

    /* Center column content vertically */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {
        width: 100%;
    }

    .new-text {
        color: #888;
        font-size: 13px;
        display: block;
        text-align: center;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    .rag-status {
        display: block;
        text-align: center;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .rag-red { color: #ff4444; }
    .rag-amber { color: #ffaa00; }
    .rag-green { color: #44ff88; }

    .rank-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 11px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .rank-beginner { background-color: #ffebee; color: #c62828; }
    .rank-developing { background-color: #fff3e0; color: #ef6c00; }
    .rank-proficient { background-color: #e8f5e9; color: #2e7d32; }
    .rank-master { background-color: #e3f2fd; color: #1565c0; }

    .stTextArea textarea {
        font-size: 16px;
        border-radius: 12px;
        border: 2px solid #333;
        background-color: #1a1a1a;
        color: #ffffff !important;
        padding: 16px;
        line-height: 1.6;
    }

    .stTextArea textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
    }

    .stTextArea textarea::placeholder {
        color: #666;
    }

    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    .score-display {
        font-size: 56px;
        font-weight: 700;
        text-align: center;
        margin: 24px 0;
        letter-spacing: -2px;
    }

    /* Override Streamlit's default button styles */
    .stButton > button[kind="primary"] {
        background-color: #4CAF50;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #45a049;
    }

    /* Success/error message styling */
    .stSuccess {
        background-color: #1a3a1a !important;
        border-left-color: #4CAF50 !important;
    }

    .stError {
        background-color: #3a1a1a !important;
        border-left-color: #ff4444 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============ COMPLETE AQA BIOLOGY A-LEVEL SPEC ============
AQA_TOPICS = {
    "3.1 Biological molecules": {
        "3.1.1 Monomers and polymers": [
            "Monomers are the smaller units from which larger molecules are made",
            "Polymers are molecules made from a large number of monomers joined together",
            "Monosaccharides, amino acids and nucleotides are examples of monomers",
            "A condensation reaction joins two molecules together with the formation of a chemical bond and involves the elimination of a molecule of water",
            "A hydrolysis reaction breaks a chemical bond between two molecules and involves the use of a water molecule"
        ],
        "3.1.2 Carbohydrates": [
            "Monosaccharides are the monomers from which larger carbohydrates are made",
            "Glucose, galactose and fructose are common monosaccharides",
            "A condensation reaction between two monosaccharides forms a glycosidic bond",
            "Maltose is a disaccharide formed by condensation of two glucose molecules",
            "Sucrose is a disaccharide formed by condensation of a glucose molecule and a fructose molecule",
            "Lactose is a disaccharide formed by condensation of a glucose molecule and a galactose molecule",
            "Glucose has two isomers, alpha-glucose and beta-glucose",
            "Polysaccharides are formed by the condensation of many glucose units",
            "Glycogen and starch are formed by the condensation of alpha-glucose",
            "Cellulose is formed by the condensation of beta-glucose",
            "The basic structure and functions of glycogen, starch and cellulose",
            "The relationship of structure to function of glycogen, starch and cellulose in animal cells and plant cells",
            "Biochemical tests using Benedict's solution for reducing sugars and non-reducing sugars",
            "Biochemical tests using iodine potassium iodide for starch"
        ],
        "3.1.3 Lipids": [
            "Triglycerides and phospholipids are two groups of lipid",
            "Triglycerides are formed by the condensation of one molecule of glycerol and three molecules of fatty acid",
            "A condensation reaction between glycerol and a fatty acid forms an ester bond",
            "The R-group of a fatty acid may be saturated or unsaturated",
            "In phospholipids, one of the fatty acids of a triglyceride is substituted by a phosphate-containing group",
            "The different properties of triglycerides and phospholipids related to their different structures",
            "The emulsion test for lipids"
        ],
        "3.1.4 Proteins": [
            "Amino acids are the monomers from which proteins are made",
            "The general structure of an amino acid as having an NH2 amine group, COOH carboxyl group and R side chain",
            "The twenty amino acids that are common in all organisms differ only in their side group",
            "A condensation reaction between two amino acids forms a peptide bond",
            "Dipeptides are formed by the condensation of two amino acids",
            "Polypeptides are formed by the condensation of many amino acids",
            "A functional protein may contain one or more polypeptides",
            "The role of hydrogen bonds, ionic bonds and disulfide bridges in the structure of proteins",
            "The relationship between primary, secondary, tertiary and quaternary structure, and protein function",
            "The biuret test for proteins"
        ],
        "3.1.5 Nucleic acids": [
            "Deoxyribonucleic acid DNA and ribonucleic acid RNA are important information-carrying molecules",
            "In all living cells, DNA holds genetic information and RNA transfers genetic information from DNA to the ribosomes",
            "Ribosomes are formed from RNA and proteins",
            "Both DNA and RNA are polymers of nucleotides",
            "Each nucleotide is formed from a pentose, a nitrogen-containing organic base and a phosphate group",
            "The components of a DNA nucleotide are deoxyribose, a phosphate group and one of the organic bases adenine, cytosine, guanine or thymine",
            "The components of an RNA nucleotide are ribose, a phosphate group and one of the organic bases adenine, cytosine, guanine or uracil",
            "A condensation reaction between two nucleotides forms a phosphodiester bond",
            "A DNA molecule is a double helix with two polynucleotide chains held together by hydrogen bonds between specific complementary base pairs",
            "An RNA molecule is a relatively short polynucleotide chain",
            "The semi-conservative replication of DNA ensures genetic continuity between generations of cells",
            "The process of semi-conservative replication of DNA in terms of unwinding of the double helix",
            "The process of semi-conservative replication of DNA in terms of breakage of hydrogen bonds between complementary bases",
            "The role of DNA helicase in unwinding DNA and breaking its hydrogen bonds",
            "The attraction of new DNA nucleotides to exposed bases on template strands and base pairing",
            "The role of DNA polymerase in the condensation reaction that joins adjacent nucleotides"
        ],
        "3.1.6 ATP": [
            "A single molecule of adenosine triphosphate ATP is a nucleotide derivative and is formed from a molecule of ribose, a molecule of adenine and three phosphate groups",
            "Hydrolysis of ATP to adenosine diphosphate ADP and an inorganic phosphate group Pi is catalysed by the enzyme ATP hydrolase",
            "The hydrolysis of ATP can be coupled to energy-requiring reactions within cells",
            "The inorganic phosphate released during the hydrolysis of ATP can be used to phosphorylate other compounds, often making them more reactive",
            "ATP is resynthesised by the condensation of ADP and Pi",
            "The resynthesis of ATP is catalysed by the enzyme ATP synthase during photosynthesis, or during respiration"
        ],
        "3.1.7 Water": [
            "Water is a major component of cells",
            "Water is a metabolite in many metabolic reactions, including condensation and hydrolysis reactions",
            "Water is an important solvent in which metabolic reactions occur",
            "Water has a relatively high heat capacity, buffering changes in temperature",
            "Water has a relatively large latent heat of vaporisation, providing a cooling effect with little loss of water through evaporation",
            "Water has strong cohesion between water molecules supporting columns of water in the tube-like transport cells of plants and producing surface tension where water meets air"
        ],
        "3.1.8 Inorganic ions": [
            "Inorganic ions occur in solution in the cytoplasm and body fluids of organisms",
            "Each type of ion has a specific role, depending on its properties",
            "Hydrogen ions and pH",
            "Iron ions as a component of haemoglobin",
            "Sodium ions in the co-transport of glucose and amino acids",
            "Phosphate ions as components of DNA and of ATP"
        ]
    },
    "3.2 Cells": {
        "3.2.1 Cell structure": [
            "The structure and function of organelles including the nucleus, mitochondria, chloroplasts, Golgi apparatus, rough and smooth endoplasmic reticulum, ribosomes, lysosomes, vacuoles, cell wall and plasma membrane",
            "The structure of prokaryotic cells including cell wall, plasma membrane, capsule, circular DNA, plasmids and flagella",
            "The structure of eukaryotic cells including nucleus, mitochondria, chloroplasts, Golgi apparatus, endoplasmic reticulum, ribosomes, lysosomes, vacuoles, cell wall and plasma membrane",
            "The differences between prokaryotic and eukaryotic cells"
        ],
        "3.2.2 All cells arise from other cells": [
            "The cell cycle including interphase, prophase, metaphase, anaphase, telophase and cytokinesis",
            "Mitosis as cell division that gives rise to genetically identical cells in which the chromosome number is maintained",
            "The role of meiosis in producing cells with a haploid number of chromosomes",
            "The events of meiosis including homologous chromosomes pairing, crossing over, separation of homologous chromosomes and separation of sister chromatids"
        ],
        "3.2.3 Transport across cell membranes": [
            "The structure of cell surface membranes as a fluid mosaic model",
            "The role of the phospholipid bilayer, proteins, cholesterol and glycolipids in membrane structure",
            "Diffusion as the net movement of particles from a region of higher concentration to a region of lower concentration",
            "Facilitated diffusion involving channel proteins and carrier proteins",
            "Osmosis as the diffusion of water from a region of higher water potential to a region of lower water potential across a partially permeable membrane",
            "Active transport as the movement of particles against a concentration gradient using energy from ATP",
            "The role of carrier proteins and co-transport in active transport",
            "Exocytosis and endocytosis as bulk transport mechanisms"
        ],
        "3.2.4 Cell recognition and the immune system": [
            "Phagocytosis by phagocytes including neutrophils and macrophages",
            "The role of T-helper cells in activating B cells",
            "B cell activation and clonal selection",
            "The role of plasma cells in antibody production",
            "The structure of antibodies as having two identical heavy polypeptide chains and two identical light polypeptide chains",
            "The primary and secondary immune response",
            "The use of monoclonal antibodies in diagnosis and treatment"
        ]
    },
    "3.3 Organisms exchange substances": {
        "3.3.1 Surface area to volume ratio": [
            "The relationship between the size of an organism and its surface area to volume ratio",
            "Changes to body shape and the development of systems in larger organisms as adaptations that facilitate exchange"
        ],
        "3.3.2 Gas exchange": [
            "Gas exchange across the body surface of a single-celled organism",
            "Gas exchange in the tracheal system of insects",
            "Gas exchange across the gills of fish including the counter-current principle",
            "Gas exchange by the leaves of dicotyledonous plants including the role of stomata",
            "The structure of the human gas exchange system including alveoli, bronchioles, bronchi, trachea and lungs",
            "The essential features of alveolar epithelium as a gas exchange surface",
            "Ventilation and gas exchange in the lungs",
            "The mechanism of breathing including the role of the diaphragm and intercostal muscles"
        ],
        "3.3.3 Digestion and absorption": [
            "The digestion of carbohydrates by amylases and membrane-bound disaccharidases",
            "The digestion of lipids by lipase including the action of bile salts",
            "The digestion of proteins by endopeptidases, exopeptidases and membrane-bound dipeptidases",
            "Co-transport mechanisms for the absorption of amino acids and monosaccharides",
            "The role of micelles in the absorption of lipids"
        ],
        "3.3.4 Mass transport": [
            "The role of haemoglobin and red blood cells in the transport of oxygen",
            "The loading, transport and unloading of oxygen in relation to the oxyhaemoglobin dissociation curve",
            "The cooperative nature of oxygen binding to haemoglobin",
            "The Bohr effect as the effect of carbon dioxide concentration on the dissociation of oxyhaemoglobin",
            "The general pattern of blood circulation in a mammal",
            "The gross structure of the human heart",
            "Pressure and volume changes during the cardiac cycle",
            "The structure of arteries, arterioles and veins in relation to their function",
            "The structure of capillaries and the importance of capillary beds",
            "The formation of tissue fluid and its return to the circulatory system",
            "Xylem as tissue that transports water in plants",
            "The cohesion-tension theory of water transport in xylem",
            "Phloem as tissue that transports organic substances in plants",
            "The mass flow hypothesis for the mechanism of translocation in plants"
        ]
    },
    "3.4 Genetic information": {
        "3.4.1 DNA, genes and chromosomes": [
            "A gene as a sequence of nucleotides that codes for a polypeptide or functional RNA",
            "The locus of a gene on a chromosome",
            "Alleles as variants of a gene",
            "The structure of chromosomes including centromere and telomeres"
        ],
        "3.4.2 DNA and protein synthesis": [
            "Transcription as the production of mRNA from a DNA template",
            "The role of RNA polymerase in transcription",
            "The splicing of pre-mRNA to remove introns and join exons",
            "Translation as the role of ribosomes, mRNA, tRNA and codons",
            "The role of start and stop codons in translation"
        ],
        "3.4.3 Genetic diversity": [
            "Meiosis and genetic variation through crossing over and independent assortment",
            "Mutations as a source of genetic variation",
            "The types of mutation including substitution, deletion, insertion, inversion and duplication"
        ],
        "3.4.4 Genetic diversity and adaptation": [
            "Natural selection as a mechanism for evolution",
            "Species as groups of organisms with similar morphology and physiology",
            "Reproductive isolation as a barrier to gene flow"
        ],
        "3.4.5 Species and taxonomy": [
            "The binomial system of naming species",
            "Courtship behaviour as part of reproductive isolation",
            "Evidence for relatedness between organisms"
        ],
        "3.4.6 Investigating diversity": [
            "The index of diversity formula",
            "Genetic diversity within and between populations"
        ]
    },
    "3.5 Energy transfers": {
        "3.5.1 Photosynthesis": [
            "The light-dependent reaction including photoionisation of chlorophyll, photolysis of water, electron transport chain, and production of ATP and reduced NADP",
            "The light-independent reaction including the Calvin cycle, carbon fixation, reduction of glycerate-3-phosphate, and regeneration of ribulose bisphosphate",
            "The factors affecting the rate of photosynthesis"
        ],
        "3.5.2 Respiration": [
            "Glycolysis including phosphorylation of glucose, lysis into triose phosphate, and oxidation to pyruvate",
            "The link reaction including decarboxylation and dehydrogenation of pyruvate to form acetylcoenzyme A",
            "The Krebs cycle including decarboxylation and dehydrogenation, substrate-level phosphorylation, and formation of reduced coenzymes",
            "The electron transport chain and oxidative phosphorylation",
            "Anaerobic respiration in animals and yeast"
        ],
        "3.5.3 Energy and ecosystems": [
            "Gross primary production and net primary production",
            "The efficiency of energy transfer between trophic levels",
            "The recycling of nitrogen and phosphorus in ecosystems"
        ],
        "3.5.4 Nutrient cycling": [
            "The role of microorganisms in decomposition",
            "The nitrogen cycle including nitrogen fixation, nitrification, denitrification and ammonification",
            "The phosphorus cycle"
        ]
    },
    "3.6 Organisms respond": {
        "3.6.1 Stimuli and responses": [
            "Survival and response including taxes, kineses and tropisms",
            "The role of IAA as an auxin in phototropism and gravitropism"
        ],
        "3.6.2 Nervous coordination": [
            "The structure and function of the mammalian nervous system",
            "The structure and function of a myelinated motor neurone",
            "The generation and transmission of action potentials",
            "Saltatory conduction",
            "The structure and function of synapses including neurotransmitters"
        ],
        "3.6.3 Muscles": [
            "The structure of skeletal muscle including myofibrils, sarcomeres, actin and myosin filaments",
            "The sliding filament mechanism of muscle contraction",
            "The role of ATP and calcium ions in muscle contraction"
        ],
        "3.6.4 Homeostasis": [
            "The principles of homeostasis including negative feedback",
            "The control of blood glucose concentration including the role of insulin and glucagon",
            "The control of blood water potential including the role of ADH and osmoreceptors"
        ]
    },
    "3.7 Genetics, populations, evolution": {
        "3.7.1 Inheritance": [
            "Genetic crosses and pedigree diagrams",
            "The chi-squared test",
            "Epistasis and lethal alleles",
            "Sex linkage and codominance"
        ],
        "3.7.2 Populations": [
            "The Hardy-Weinberg principle and equation",
            "Selection pressures and directional, stabilising and disruptive selection"
        ],
        "3.7.3 Evolution": [
            "Speciation including allopatric and sympatric speciation",
            "Genetic drift and the bottleneck effect",
            "The founder effect"
        ],
        "3.7.4 Ecosystems": [
            "Succession including primary and secondary succession",
            "The conservation of habitats and species"
        ]
    },
    "3.8 The control of gene expression": {
        "3.8.1 Mutations and gene expression": [
            "The types of gene mutation including substitution, deletion and insertion",
            "The effect of mutations on protein structure and function",
            "Oncogenes and tumour suppressor genes"
        ],
        "3.8.2 Regulation of gene expression": [
            "Transcription factors and gene expression",
            "Oestrogen and the regulation of gene expression",
            "SiRNA and gene silencing"
        ],
        "3.8.3 Using genome projects": [
            "Gene sequencing and genome sequencing",
            "Bioinformatics and understanding of gene function"
        ],
        "3.8.4 Gene technologies": [
            "Recombinant DNA technology including restriction endonucleases, ligases and plasmids",
            "In vivo and in vitro gene cloning",
            "Genetic fingerprinting and PCR"
        ]
    }
}

# ============ DATA PERSISTENCE ============
DATA_FILE = "bioblurt_progress.json"

def load_progress():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(DATA_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

# ============ SMART SCORING ENGINE ============
STOP_WORDS = {
    'the', 'and', 'are', 'from', 'that', 'with', 'for', 'can', 'its', 'has',
    'have', 'this', 'into', 'been', 'they', 'their', 'them', 'than', 'then',
    'when', 'where', 'which', 'while', 'during', 'between', 'through', 'within',
    'under', 'over', 'such', 'each', 'both', 'all', 'any', 'some', 'many',
    'most', 'more', 'less', 'very', 'also', 'only', 'just', 'but', 'not',
    'however', 'therefore', 'because', 'since', 'although', 'though', 'unless',
    'whether', 'either', 'neither', 'both', 'either', 'nor', 'yet', 'so',
    'as', 'at', 'by', 'in', 'of', 'on', 'to', 'up', 'via', 'per', 'a', 'an',
    'is', 'it', 'be', 'or', 'if', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'was', 'were', 'had', 'has',
    'having', 'being', 'made', 'used', 'using', 'form', 'forms', 'formed',
    'role', 'roles', 'function', 'functions', 'structure', 'structures',
    'process', 'processes', 'including', 'involves', 'involving', 'including'
}

def extract_keywords(text):
    """Extract meaningful keywords from text, removing stop words."""
    words = text.lower().split()
    keywords = []
    for word in words:
        clean = ''.join(c for c in word if c.isalnum())
        if len(clean) >= 3 and clean not in STOP_WORDS:
            keywords.append(clean)
    return keywords

def similarity_score(user_keywords, point_keywords):
    """Calculate fuzzy similarity between two sets of keywords."""
    if not point_keywords:
        return 0.0

    matched = 0
    for pk in point_keywords:
        best_match = 0
        for uk in user_keywords:
            # Exact match
            if pk == uk:
                best_match = 1.0
                break
            # Contains match (e.g., "monosaccharide" contains "saccharide")
            elif pk in uk or uk in pk:
                best_match = max(best_match, 0.8)
            # Fuzzy match for typos/close words
            else:
                ratio = SequenceMatcher(None, pk, uk).ratio()
                if ratio > 0.75:
                    best_match = max(best_match, ratio)

        if best_match > 0.5:
            matched += best_match

    return matched / len(point_keywords)

def calculate_score(user_text, spec_points):
    """Score user blurt against spec points using smart keyword matching."""
    if not user_text or not user_text.strip():
        return 0.0, []

    user_keywords = extract_keywords(user_text)
    if not user_keywords:
        return 0.0, []

    matched_points = []
    total_points = len(spec_points)

    for point in spec_points:
        point_keywords = extract_keywords(point)
        sim = similarity_score(user_keywords, point_keywords)

        # Point is "matched" if similarity >= 40%
        if sim >= 0.4:
            matched_points.append(point)

    score = (len(matched_points) / total_points * 100) if total_points > 0 else 0
    return round(min(score, 100), 1), matched_points

# ============ RANKING & RAG ============
def get_rank(percentage):
    if percentage < 30:
        return "Beginner", "rank-beginner"
    elif percentage < 50:
        return "Developing", "rank-developing"
    elif percentage < 70:
        return "Proficient", "rank-proficient"
    else:
        return "Master", "rank-master"

def get_rag_status(score, manual_rag=None):
    """Get RAG status. Uses manual override if set, otherwise score-based."""
    if manual_rag:
        colors = {"Red": "rag-red", "Amber": "rag-amber", "Green": "rag-green"}
        return manual_rag, colors.get(manual_rag, "rag-red")

    if score < 40:
        return "Red", "rag-red"
    elif score < 65:
        return "Amber", "rag-amber"
    else:
        return "Green", "rag-green"

# ============ SESSION STATE ============
if 'progress' not in st.session_state:
    st.session_state.progress = load_progress()

if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None

if 'selected_subtopic' not in st.session_state:
    st.session_state.selected_subtopic = None

if 'current_score' not in st.session_state:
    st.session_state.current_score = 0

# ============ UI ============
st.title("🧬 BioBlurt")
st.markdown("<p style='text-align: center; color: #888; margin-top: -10px; font-size: 14px;'>Active Recall for AQA A-Level Biology</p>", unsafe_allow_html=True)
st.markdown("---")

# ============ NAVIGATION ============
if st.session_state.selected_subtopic is None:
    # Topic selection screen
    if st.session_state.selected_topic is None:
        st.subheader("Select a Topic")

        for topic_name, subtopics in AQA_TOPICS.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📚 {topic_name}", key=f"topic_{topic_name}", use_container_width=True):
                    st.session_state.selected_topic = topic_name
                    st.rerun()
            with col2:
                topic_scores = []
                for sub in subtopics:
                    key = f"{topic_name}|{sub}"
                    if key in st.session_state.progress:
                        topic_scores.append(st.session_state.progress[key].get('score', 0))
                if topic_scores:
                    avg = sum(topic_scores) / len(topic_scores)
                    manual = None
                    for sub in subtopics:
                        k = f"{topic_name}|{sub}"
                        if k in st.session_state.progress and st.session_state.progress[k].get('rag'):
                            manual = st.session_state.progress[k].get('rag')
                            break
                    status, css_class = get_rag_status(avg, manual)
                    st.markdown(f"<span class='rag-status {css_class}'>{status}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='new-text'>New</span>", unsafe_allow_html=True)
    else:
        # Subtopic selection screen
        st.subheader(f"📚 {st.session_state.selected_topic}")

        if st.button("← Back to Topics", key="back_to_topics"):
            st.session_state.selected_topic = None
            st.rerun()

        st.markdown("---")
        st.markdown("**Select a sub-topic to blurt:**")

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
                    score = st.session_state.progress[key].get('score', 0)
                    manual = st.session_state.progress[key].get('rag', None)
                    status, css_class = get_rag_status(score, manual)
                    st.markdown(f"<span class='rag-status {css_class}'>{status}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='new-text'>New</span>", unsafe_allow_html=True)
            with col3:
                key = f"{st.session_state.selected_topic}|{subtopic_name}"
                if key in st.session_state.progress:
                    score = st.session_state.progress[key].get('score', 0)
                    rank, rank_class = get_rank(score)
                    st.markdown(f"<div style='text-align: center; padding-top: 2px;'><span class='rank-badge {rank_class}'>{rank}</span></div>", unsafe_allow_html=True)

else:
    # Blurting screen
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
        if st.button("🏠 Home", key="go_home"):
            st.session_state.selected_topic = None
            st.session_state.selected_subtopic = None
            st.session_state.current_score = 0
            st.rerun()

    st.markdown("---")

    # Show current status
    progress_key = f"{topic}|{subtopic}"
    if progress_key in st.session_state.progress:
        current_data = st.session_state.progress[progress_key]
        current_score = current_data.get('score', 0)
        manual_rag = current_data.get('rag', None)
        status, css_class = get_rag_status(current_score, manual_rag)
        rank, rank_class = get_rank(current_score)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Current Status:** <span class='{css_class}'>{status}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Best Score:** {current_score}%")
        with col3:
            st.markdown(f"<span class='rank-badge {rank_class}'>{rank}</span>", unsafe_allow_html=True)
        st.markdown("---")

    # Blurt input
    st.markdown("### 🧠 Blurt everything you know about this topic:")
    st.markdown("<p style='color: #888; font-size: 14px;'>Type everything you can remember. Don't worry about perfect sentences — just get the key concepts down!</p>", unsafe_allow_html=True)

    user_blurt = st.text_area(
        "",
        height=300,
        placeholder="Start typing your blurt here...",
        key="blurt_input"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✅ Submit Blurt", type="primary", use_container_width=True):
            if user_blurt.strip():
                score, matched = calculate_score(user_blurt, spec_points)
                st.session_state.current_score = score

                progress_key = f"{topic}|{subtopic}"
                existing = st.session_state.progress.get(progress_key, {})
                st.session_state.progress[progress_key] = {
                    "score": score,
                    "rag": existing.get('rag', get_rag_status(score)[0]),
                    "last_attempt": datetime.now().isoformat(),
                    "attempts": existing.get("attempts", 0) + 1
                }
                save_progress(st.session_state.progress)
                st.rerun()
            else:
                st.error("Please write something before submitting!")

    # Show results
    if st.session_state.current_score > 0 or progress_key in st.session_state.progress:
        if st.session_state.current_score > 0:
            display_score = st.session_state.current_score
        else:
            display_score = st.session_state.progress[progress_key].get('score', 0)

        st.markdown("---")
        st.markdown("### 📊 Results")

        manual_rag = st.session_state.progress.get(progress_key, {}).get('rag', None)
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
                st.markdown("🔴 **Red** — Keep studying this topic!")
            elif display_score < 65:
                st.markdown("🟡 **Amber** — Getting there, review missed points")
            else:
                st.markdown("🟢 **Green** — Great recall! Move to next topic")

        # Spec points breakdown
        st.markdown("---")
        st.markdown("### 📝 Specification Points Check")

        _, matched = calculate_score(user_blurt if user_blurt.strip() else "", spec_points)

        for point in spec_points:
            if point in matched:
                st.success(f"✅ {point}")
            else:
                st.error(f"❌ {point}")

        # Manual RAG override — FIXED
        st.markdown("---")
        st.markdown("### 🎯 Manual RAG Assessment")
        st.markdown("<p style='color: #888; font-size: 13px;'>How do YOU feel about this topic? Override the auto-score below.</p>", unsafe_allow_html=True)

        rag_col1, rag_col2, rag_col3 = st.columns(3)
        with rag_col1:
            if st.button("🔴 Red", key="manual_red", use_container_width=True):
                progress_key = f"{topic}|{subtopic}"
                if progress_key not in st.session_state.progress:
                    st.session_state.progress[progress_key] = {}
                st.session_state.progress[progress_key]['rag'] = "Red"
                save_progress(st.session_state.progress)
                st.success("Set to Red!")
                st.rerun()
        with rag_col2:
            if st.button("🟡 Amber", key="manual_amber", use_container_width=True):
                progress_key = f"{topic}|{subtopic}"
                if progress_key not in st.session_state.progress:
                    st.session_state.progress[progress_key] = {}
                st.session_state.progress[progress_key]['rag'] = "Amber"
                save_progress(st.session_state.progress)
                st.success("Set to Amber!")
                st.rerun()
        with rag_col3:
            if st.button("🟢 Green", key="manual_green", use_container_width=True):
                progress_key = f"{topic}|{subtopic}"
                if progress_key not in st.session_state.progress:
                    st.session_state.progress[progress_key] = {}
                st.session_state.progress[progress_key]['rag'] = "Green"
                save_progress(st.session_state.progress)
                st.success("Set to Green!")
                st.rerun()

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #555; font-size: 12px;'>BioBlurt v2.0 | AQA Biology A-Level (7402) | Built with Streamlit</p>", unsafe_allow_html=True)
