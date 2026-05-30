
import streamlit as st
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
import streamlit.components.v1 as components

components.html(
    """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-76RQM2X7BW"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-76RQM2X7BW');
    </script>
    """,
    height=0,
)

# PWA support
st.markdown("""
    <link rel="manifest" href="manifest.json">
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('sw.js');
        }
    </script>
""", unsafe_allow_html=True)

# Page config - minimalistic Anki-style
st.set_page_config(
    page_title="BioBlurt - AQA Biology Active Recall",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimalistic Anki-style look
st.markdown("""
<style>
    .main {
        background-color: #fafafa;
    }
    .stTextArea textarea {
        font-size: 16px;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        background-color: black;
    }
    .stTextArea textarea:focus {
        border-color: #999999;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .topic-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .topic-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .rag-red { color: #f44336; font-weight: bold; }
    .rag-amber { color: #ff9800; font-weight: bold; }
    .rag-green { color: #4CAF50; font-weight: bold; }
    .score-display {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
    .rank-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        margin-top: 10px;
    }
    .rank-beginner { background-color: #ffebee; color: #c62828; }
    .rank-developing { background-color: #fff3e0; color: #ef6c00; }
    .rank-proficient { background-color: #e8f5e9; color: #2e7d32; }
    .rank-master { background-color: #e3f2fd; color: #1565c0; }
</style>
""", unsafe_allow_html=True)

# AQA Biology A-Level Specification Data
AQA_TOPICS = {
    "1.0 Biological molecules": {
        "1.1 Monomers and polymers": [
            "Monomers are smaller units from which larger molecules (polymers) are made",
            "Polymers are molecules made from a large number of monomers joined together",
            "Monosaccharides, amino acids and nucleotides are examples of monomers",
            "A condensation reaction joins two molecules together with formation of a chemical bond and involves elimination of water",
            "A hydrolysis reaction breaks a chemical bond between two molecules and involves use of a water molecule"
        ],
        "1.2 Carbohydrates": [
            "Monosaccharides are the monomers from which larger carbohydrates are made",
            "Glucose, galactose and fructose are common monosaccharides",
            "A condensation reaction between two monosaccharides forms a glycosidic bond",
            "Maltose is a disaccharide formed by condensation of two glucose molecules",
            "Sucrose is a disaccharide formed by condensation of a glucose and a fructose molecule",
            "Lactose is a disaccharide formed by condensation of a glucose and a galactose molecule",
            "Glucose has two isomers: alpha-glucose and beta-glucose",
            "Polysaccharides are formed by condensation of many glucose units",
            "Glycogen and starch are formed by condensation of alpha-glucose",
            "Cellulose is formed by condensation of beta-glucose",
            "Basic structure and functions of glycogen, starch and cellulose",
            "Relationship of structure to function of glycogen, starch and cellulose in animal and plant cells",
            "Benedict's solution test for reducing sugars and non-reducing sugars",
            "Iodine/potassium iodide test for starch"
        ],
        "1.3 Lipids": [
            "Triglycerides and phospholipids are two groups of lipid",
            "Triglycerides are formed by condensation of one glycerol and three fatty acids",
            "A condensation reaction between glycerol and a fatty acid forms an ester bond",
            "The R-group of a fatty acid may be saturated or unsaturated",
            "In phospholipids, one fatty acid of a triglyceride is substituted by a phosphate-containing group",
            "Different properties of triglycerides and phospholipids related to their different structures",
            "The emulsion test for lipids"
        ],
        "1.4 Proteins": [
            "Amino acids are the monomers from which proteins are made",
            "General structure of an amino acid with NH2 amine group, COOH carboxyl group and R side chain",
            "Twenty amino acids common in all organisms differ only in their side group",
            "A condensation reaction between two amino acids forms a peptide bond",
            "Dipeptides are formed by condensation of two amino acids",
            "Polypeptides are formed by condensation of many amino acids",
            "A functional protein may contain one or more polypeptides",
            "Role of hydrogen bonds, ionic bonds and disulfide bridges in protein structure",
            "Relationship between primary, secondary, tertiary and quaternary structure and protein function",
            "The biuret test for proteins"
        ],
        "1.5 Nucleic acids": [
            "DNA and RNA are important information-carrying molecules",
            "DNA holds genetic information and RNA transfers genetic information from DNA to ribosomes",
            "Ribosomes are formed from RNA and proteins",
            "Both DNA and RNA are polymers of nucleotides",
            "Each nucleotide is formed from a pentose, a nitrogen-containing organic base and a phosphate group",
            "DNA nucleotide components: deoxyribose, phosphate group, organic bases adenine cytosine guanine thymine",
            "RNA nucleotide components: ribose, phosphate group, organic bases adenine cytosine guanine uracil",
            "A condensation reaction between two nucleotides forms a phosphodiester bond",
            "DNA molecule is a double helix with two polynucleotide chains held together by hydrogen bonds between complementary base pairs",
            "RNA molecule is a relatively short polynucleotide chain",
            "Semi-conservative replication of DNA ensures genetic continuity between generations of cells",
            "Role of DNA helicase in unwinding DNA and breaking hydrogen bonds",
            "Role of DNA polymerase in joining adjacent nucleotides"
        ],
        "1.6 ATP": [
            "ATP is a nucleotide derivative formed from ribose, adenine and three phosphate groups",
            "Hydrolysis of ATP to ADP and Pi is catalysed by ATP hydrolase",
            "Hydrolysis of ATP can be coupled to energy-requiring reactions within cells",
            "Inorganic phosphate released during hydrolysis can be used to phosphorylate other compounds",
            "ATP is resynthesised by condensation of ADP and Pi catalysed by ATP synthase during photosynthesis or respiration"
        ],
        "1.7 Water": [
            "Water is a metabolite in many metabolic reactions including condensation and hydrolysis",
            "Water is an important solvent in which metabolic reactions occur",
            "Water has a relatively high heat capacity, buffering changes in temperature",
            "Water has a relatively large latent heat of vaporisation, providing cooling effect with little water loss",
            "Water has strong cohesion between molecules supporting columns of water in plant transport cells and producing surface tension"
        ],
        "1.8 Inorganic ions": [
            "Inorganic ions occur in solution in cytoplasm and body fluids",
            "Hydrogen ions and pH",
            "Iron ions as a component of haemoglobin",
            "Sodium ions in the co-transport of glucose and amino acids",
            "Phosphate ions as components of DNA and ATP"
        ]
    },
    "2.0 Cells": {
        "2.1 Cell structure": [
            "Structure and function of organelles including nucleus, mitochondria, chloroplasts, Golgi apparatus, ER, ribosomes, lysosomes, vacuoles, cell wall, plasma membrane",
            "Prokaryotic and eukaryotic cell structure differences",
            "Structure of bacteria including cell wall, plasma membrane, capsule, circular DNA, plasmids, flagella"
        ],
        "2.2 All cells arise from other cells": [
            "Cell division by mitosis and meiosis",
            "The cell cycle: interphase, prophase, metaphase, anaphase, telophase, cytokinesis"
        ],
        "2.3 Transport across cell membranes": [
            "Structure of cell surface membrane as fluid mosaic model",
            "Passive transport: diffusion, facilitated diffusion, osmosis",
            "Active transport",
            "Bulk transport: exocytosis and endocytosis"
        ],
        "2.4 Cell recognition and the immune system": [
            "Phagocytosis by phagocytes",
            "T-helper cell activation of B cells",
            "B cell activation and clonal selection",
            "Plasma cells and antibody production",
            "Primary and secondary immune response",
            "Monoclonal antibodies and their use in diagnosis and treatment"
        ]
    },
    "3.0 Organisms exchange substances": {
        "3.1 Surface area to volume ratio": [
            "Relationship between size of organism and surface area to volume ratio",
            "Changes to body shape and development of systems as adaptations facilitating exchange"
        ],
        "3.2 Gas exchange": [
            "Gas exchange across body surface of single-celled organism",
            "Gas exchange in tracheal system of insects",
            "Gas exchange across gills of fish including counter-current principle",
            "Gas exchange by leaves of dicotyledonous plants",
            "Structure of human gas exchange system: alveoli, bronchioles, bronchi, trachea, lungs",
            "Essential features of alveolar epithelium",
            "Ventilation and gas exchange in lungs",
            "Mechanism of breathing including role of diaphragm and intercostal muscles"
        ],
        "3.3 Digestion and absorption": [
            "Digestion of carbohydrates by amylases and membrane-bound disaccharidases",
            "Digestion of lipids by lipase including action of bile salts",
            "Digestion of proteins by endopeptidases, exopeptidases and membrane-bound dipeptidases",
            "Co-transport mechanisms for absorption of amino acids and monosaccharides",
            "Role of micelles in absorption of lipids"
        ],
        "3.4 Mass transport": [
            "Role of haemoglobin and red blood cells in transport of oxygen",
            "Loading, transport and unloading of oxygen in relation to oxyhaemoglobin dissociation curve",
            "Cooperative nature of oxygen binding to haemoglobin",
            "Bohr effect: effect of carbon dioxide concentration on dissociation of oxyhaemoglobin",
            "General pattern of blood circulation in a mammal",
            "Gross structure of the human heart",
            "Pressure and volume changes during cardiac cycle",
            "Structure of arteries, arterioles and veins in relation to function",
            "Structure of capillaries and importance of capillary beds",
            "Formation of tissue fluid and its return to circulatory system",
            "Xylem as tissue that transports water in plants",
            "Cohesion-tension theory of water transport in xylem",
            "Phloem as tissue that transports organic substances in plants",
            "Mass flow hypothesis for mechanism of translocation in plants"
        ]
    },
    "4.0 Genetic information": {
        "4.1 DNA, genes and chromosomes": [
            "Gene as a sequence of nucleotides that codes for a polypeptide or functional RNA",
            "Locus of a gene on a chromosome",
            "Alleles as variants of a gene",
            "Structure of chromosomes including centromere and telomeres"
        ],
        "4.2 DNA and protein synthesis": [
            "Transcription: production of mRNA from DNA template",
            "Role of RNA polymerase in transcription",
            "Splicing of pre-mRNA to remove introns and join exons",
            "Translation: role of ribosomes, mRNA, tRNA and codons",
            "Role of start and stop codons"
        ],
        "4.3 Genetic diversity": [
            "Meiosis and genetic variation through crossing over and independent assortment",
            "Mutations as source of genetic variation",
            "Types of mutation: substitution, deletion, insertion, inversion, duplication"
        ],
        "4.4 Genetic diversity and adaptation": [
            "Natural selection as mechanism for evolution",
            "Species as groups of organisms with similar morphology and physiology",
            "Reproductive isolation as barrier to gene flow"
        ],
        "4.5 Species and taxonomy": [
            "Binomial system of naming species",
            "Courtship behaviour as part of reproductive isolation",
            "Evidence for relatedness between organisms"
        ],
        "4.6 Investigating diversity": [
            "Index of diversity formula",
            "Genetic diversity within and between populations"
        ]
    },
    "5.0 Energy transfers": {
        "5.1 Photosynthesis": [
            "Light-dependent reaction: photoionisation of chlorophyll, photolysis of water, electron transport chain, production of ATP and reduced NADP",
            "Light-independent reaction: Calvin cycle, carbon fixation, reduction of glycerate-3-phosphate, regeneration of ribulose bisphosphate",
            "Factors affecting rate of photosynthesis"
        ],
        "5.2 Respiration": [
            "Glycolysis: phosphorylation of glucose, lysis into triose phosphate, oxidation to pyruvate",
            "Link reaction: decarboxylation and dehydrogenation of pyruvate to form acetylcoenzyme A",
            "Krebs cycle: decarboxylation and dehydrogenation, substrate-level phosphorylation, formation of reduced coenzymes",
            "Electron transport chain and oxidative phosphorylation",
            "Anaerobic respiration in animals and yeast"
        ],
        "5.3 Energy and ecosystems": [
            "Gross primary production and net primary production",
            "Efficiency of energy transfer between trophic levels",
            "Recycling of nitrogen and phosphorus in ecosystems"
        ],
        "5.4 Nutrient cycling": [
            "Role of microorganisms in decomposition",
            "Nitrogen cycle: nitrogen fixation, nitrification, denitrification, ammonification",
            "Phosphorus cycle"
        ]
    },
    "6.0 Organisms respond": {
        "6.1 Stimuli and responses": [
            "Survival and response: taxes, kineses and tropisms",
            "Role of IAA as auxin in phototropism and gravitropism"
        ],
        "6.2 Nervous coordination": [
            "Structure and function of mammalian nervous system",
            "Structure and function of myelinated motor neurone",
            "Generation and transmission of action potentials",
            "Saltatory conduction",
            "Structure and function of synapses including neurotransmitters"
        ],
        "6.3 Muscles": [
            "Structure of skeletal muscle: myofibrils, sarcomeres, actin and myosin filaments",
            "Sliding filament mechanism of muscle contraction",
            "Role of ATP and calcium ions in muscle contraction"
        ],
        "6.4 Homeostasis": [
            "Principles of homeostasis: negative feedback",
            "Control of blood glucose concentration including role of insulin and glucagon",
            "Control of blood water potential including role of ADH and osmoreceptors"
        ]
    },
    "7.0 Genetics and populations": {
        "7.1 Inheritance": [
            "Genetic crosses and pedigree diagrams",
            "Chi-squared test",
            "Epistasis and lethal alleles",
            "Sex linkage and codominance"
        ],
        "7.2 Populations": [
            "Hardy-Weinberg principle and equation",
            "Selection pressures and directional, stabilising and disruptive selection"
        ],
        "7.3 Evolution": [
            "Speciation: allopatric and sympatric",
            "Genetic drift and bottleneck effect",
            "Founder effect"
        ],
        "7.4 Ecosystems": [
            "Succession: primary and secondary",
            "Conservation of habitats and species"
        ]
    },
    "8.0 Gene expression": {
        "8.1 Mutations and gene expression": [
            "Types of gene mutation: substitution, deletion, insertion",
            "Effect of mutations on protein structure and function",
            "Oncogenes and tumour suppressor genes"
        ],
        "8.2 Regulation of gene expression": [
            "Transcription factors and gene expression",
            "Oestrogen and regulation of gene expression",
            "SiRNA and gene silencing"
        ],
        "8.3 Using genome projects": [
            "Gene sequencing and genome sequencing",
            "Bioinformatics and understanding of gene function"
        ],
        "8.4 Gene technologies": [
            "Recombinant DNA technology: restriction endonucleases, ligases, plasmids",
            "In vivo and in vitro gene cloning",
            "Genetic fingerprinting and PCR"
        ]
    }
}

# Data file for progress tracking
DATA_FILE = "bioblurt_progress.json"

def load_progress():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(DATA_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def get_rank(percentage):
    if percentage < 40:
        return "Beginner", "rank-beginner"
    elif percentage < 60:
        return "Developing", "rank-developing"
    elif percentage < 80:
        return "Proficient", "rank-proficient"
    else:
        return "Master", "rank-master"

def calculate_score(user_text, spec_points):
    if not user_text.strip():
        return 0, []

    user_lower = user_text.lower()
    matched_points = []
    total_points = len(spec_points)

    for point in spec_points:
        # Extract key terms from spec point (words > 4 chars or important biological terms)
        key_terms = []
        words = point.lower().split()
        for word in words:
            clean = ''.join(c for c in word if c.isalnum())
            if len(clean) > 4 or clean in ['dna', 'rna', 'atp', 'nad', 'fadh']:
                key_terms.append(clean)

        # Check if any key terms are in user text
        matches = sum(1 for term in key_terms if term in user_lower)
        if matches >= max(1, len(key_terms) * 0.3):  # At least 30% of key terms
            matched_points.append(point)

    score = len(matched_points) / total_points * 100 if total_points > 0 else 0
    return round(score, 1), matched_points

def get_rag_status(score):
    if score < 50:
        return "Red", "rag-red"
    elif score < 75:
        return "Amber", "rag-amber"
    else:
        return "Green", "rag-green"

# Initialize session state
if 'progress' not in st.session_state:
    st.session_state.progress = load_progress()

if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None

if 'selected_subtopic' not in st.session_state:
    st.session_state.selected_subtopic = None

if 'current_score' not in st.session_state:
    st.session_state.current_score = 0

# Main app
st.title("🧬 BioBlurt")
st.markdown("<p style='text-align: center; color: #666; margin-top: -10px;'>Active Recall for AQA A-Level Biology</p>", unsafe_allow_html=True)
st.markdown("---")

# Navigation
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
                # Show average progress for topic
                topic_scores = []
                for sub in subtopics:
                    key = f"{topic_name}|{sub}"
                    if key in st.session_state.progress:
                        topic_scores.append(st.session_state.progress[key]['score'])
                if topic_scores:
                    avg = sum(topic_scores) / len(topic_scores)
                    status, css_class = get_rag_status(avg)
                    st.markdown(f"<span class='{css_class}'>{status}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color: #999;'>New</span>", unsafe_allow_html=True)
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
                    score = st.session_state.progress[key]['score']
                    status, css_class = get_rag_status(score)
                    st.markdown(f"<span class='{css_class}'>{status}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color: #999;'>New</span>", unsafe_allow_html=True)
            with col3:
                key = f"{st.session_state.selected_topic}|{subtopic_name}"
                if key in st.session_state.progress:
                    score = st.session_state.progress[key]['score']
                    rank, rank_class = get_rank(score)
                    st.markdown(f"<span class='rank-badge {rank_class}'>{rank}</span>", unsafe_allow_html=True)

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

    # Show current status if exists
    progress_key = f"{topic}|{subtopic}"
    if progress_key in st.session_state.progress:
        current_data = st.session_state.progress[progress_key]
        current_score = current_data['score']
        status, css_class = get_rag_status(current_score)
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
    st.markdown("<p style='color: #666; font-size: 14px;'>Type everything you can remember. Don't worry about perfect sentences - just get the key concepts down!</p>", unsafe_allow_html=True)

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

                # Save progress
                progress_key = f"{topic}|{subtopic}"
                st.session_state.progress[progress_key] = {
                    "score": score,
                    "rag": get_rag_status(score)[0],
                    "last_attempt": datetime.now().isoformat(),
                    "attempts": st.session_state.progress.get(progress_key, {}).get("attempts", 0) + 1
                }
                save_progress(st.session_state.progress)

                st.rerun()
            else:
                st.error("Please write something before submitting!")

    # Show results if available
    if st.session_state.current_score > 0 or progress_key in st.session_state.progress:
        display_score = st.session_state.current_score if st.session_state.current_score > 0 else st.session_state.progress[progress_key]['score']

        st.markdown("---")
        st.markdown("### 📊 Results")

        status, css_class = get_rag_status(display_score)
        rank, rank_class = get_rank(display_score)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='score-display {css_class}'>{display_score}%</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'><span class='rank-badge {rank_class}'>{rank}</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("**Status:**")
            st.markdown(f"<span class='{css_class}' style='font-size: 24px;'>{status}</span>", unsafe_allow_html=True)

            if display_score < 50:
                st.markdown("🔴 **Red** - Keep studying this topic!")
            elif display_score < 70:
                st.markdown("🟡 **Amber** - Getting there, review missed points")
            else:
                st.markdown("🟢 **Green** - Great recall! Move to next topic")

        # Show spec points breakdown
        st.markdown("---")
        st.markdown("### 📝 Specification Points Check")

        _, matched = calculate_score(user_blurt if user_blurt.strip() else "", spec_points)

        for point in spec_points:
            if point in matched:
                st.success(f"✅ {point}")
            else:
                st.error(f"❌ {point}")

        # RAG selector for manual override
        st.markdown("---")
        st.markdown("### 🎯 Manual RAG Assessment")
        st.markdown("How do YOU feel about this topic?")

        rag_col1, rag_col2, rag_col3 = st.columns(3)
        with rag_col1:
            if st.button("🔴 Red", use_container_width=True):
                st.session_state.progress[progress_key]['rag'] = "Red"
                save_progress(st.session_state.progress)
                st.success("Set to Red!")
        with rag_col2:
            if st.button("🟡 Amber", use_container_width=True):
                st.session_state.progress[progress_key]['rag'] = "Amber"
                save_progress(st.session_state.progress)
                st.success("Set to Amber!")
        with rag_col3:
            if st.button("🟢 Green", use_container_width=True):
                st.session_state.progress[progress_key]['rag'] = "Green"
                save_progress(st.session_state.progress)
                st.success("Set to Green!")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 12px;'>BioBlurt v1.0 | AQA Biology A-Level (7402) | Built with Streamlit</p>", unsafe_allow_html=True)
