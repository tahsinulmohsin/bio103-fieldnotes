# Module 04: Central Dogma of Molecular Biology (27 Slides)

CURATED_SLIDES = {
    1: {
        "title": "Introduction: The Central Dogma of Molecular Biology",
        "explanation": """**The Central Dogma** represents the unifying framework of molecular genetics:

### Fundamental Paradigm
- **Directional Flow of Genetic Information:** Genetic blueprints stored in DNA are transcribed into messenger RNA, which is then translated into functional polypeptides.
- **Formulated by Francis Crick (1958):** Information encoded in nucleic acid sequences can be replicated or transferred to proteins, but once information has passed into a protein, it cannot get out again."""
    },
    2: {
        "title": "The Central Dogma Flowchart: DNA to RNA to Protein",
        "explanation": """Genetic information flows through three coordinated molecular stages:

### Three Fundamental Processes
1. **DNA Replication:** Faithful duplication of genomic DNA during S-phase of the cell cycle to ensure hereditary continuity.
2. **Transcription:** Enzymatic synthesis of complementary messenger RNA (mRNA) from a DNA template strand.
3. **Translation:** Ribosomal decoding of mRNA codons into a specific sequence of amino acids, forming a functional protein."""
    },
    3: {
        "title": "Francis Crick's Central Dogma Framework",
        "explanation": """The core theoretical distinction established by Francis Crick:

### Sequence Information Transfer
- **Nucleic Acid to Nucleic Acid:** DNA $\\rightarrow$ DNA (Replication) and DNA $\\rightarrow$ RNA (Transcription).
- **Nucleic Acid to Protein:** RNA $\\rightarrow$ Protein (Translation) via the genetic code.
- **The Irreversible Step:** Protein sequences cannot serve as templates to synthesize nucleic acids or alter the genomic sequence."""
    },
    4: {
        "title": "Nuclear Architecture & Chromatin Organization",
        "explanation": """In eukaryotic cells, genomic DNA is compartmentalized within the double-membraned nucleus:

### Structural Organization
- **Nuclear Envelope:** Double lipid bilayer perforated by **nuclear pores** that regulate macromolecular transit (RNA export, protein import).
- **Chromatin:** DNA complexed with basic **histone proteins** forming nucleosomes ("beads-on-a-string").
- **Euchromatin vs. Heterochromatin:** Loosely packed euchromatin is transcriptionally active, whereas densely condensed heterochromatin remains transcriptionally silent."""
    },
    5: {
        "title": "Molecular Structure of the DNA Double Helix",
        "explanation": """Elucidated by James Watson and Francis Crick in 1953:

### Structural Features
- **Double Helix:** Two polynucleotide strands wound around a central axis in a right-handed spiral.
- **Antiparallel Strands:** One strand runs in the $5' \\rightarrow 3'$ direction, while the complementary strand runs $3' \\rightarrow 5'$.
- **Sugar-Phosphate Backbone:** Deoxyribose sugars joined by covalent **phosphodiester bonds** form the exterior scaffold, while nitrogenous bases point inward."""
    },
    6: {
        "title": "Complementary Base Pairing (Chargaff's Rules)",
        "explanation": """Specific hydrogen bonding between complementary nitrogenous bases stabilizes the double helix:

### Base-Pairing Rules
- **Adenine pairs with Thymine ($A = T$):** Joined by **two hydrogen bonds**.
- **Guanine pairs with Cytosine ($G \\equiv C$):** Joined by **three hydrogen bonds** (requiring higher thermal energy to denature).
- **Chargaff's Law:** In double-stranded DNA, the ratio of purines equals pyrimidines ($[A] = [T]$ and $[G] = [C]$)."""
    },
    7: {
        "title": "Semi-Conservative DNA Replication",
        "explanation": """Demonstrated experimentally by Matthew Meselson and Franklin Stahl (1958):

### The Semi-Conservative Mechanism
- During replication, the two parent strands separate, and each serves as an exact template for the synthesis of a complementary daughter strand.
- **Outcome:** Each replicated double helix consists of **one conserved parental strand** and **one newly synthesized daughter strand**."""
    },
    8: {
        "title": "Replication Fork & Helicase Unwinding",
        "explanation": """Replication initiates at designated chromosomal loci termed **origins of replication**:

### Fork Machinery
- **DNA Helicase:** Consumes ATP to break hydrogen bonds between base pairs, unwinding the double helix into a **replication fork**.
- **Single-Stranded Binding Proteins (SSBs):** Coat single strands to prevent premature re-annealing.
- **Topoisomerase (DNA Gyrase):** Relieves downstream torsional strain and supercoiling caused by helicase unwinding."""
    },
    9: {
        "title": "DNA Polymerase III & RNA Primase",
        "explanation": """DNA polymerases synthesize new DNA strands but possess strict biochemical constraints:

### Catalytic Requirements
- **$5' \\rightarrow 3'$ Directionality:** DNA polymerases can only append new deoxynucleotides (dNTPs) to the free $3'\\text{-OH}$ group of a growing strand.
- **Requirement for RNA Primase:** DNA polymerase cannot initiate synthesis *de novo*; **RNA primase** must first lay down a short RNA primer to provide a starting $3'\\text{-OH}$ terminus."""
    },
    10: {
        "title": "Leading vs. Lagging Strand Synthesis",
        "explanation": """Because the replication fork advances unidirectionally while strands are antiparallel, synthesis proceeds asymmetrically:

### Dual Strand Mechanics
- **Leading Strand:** Synthesized **continuously** toward the progressing replication fork in the $5' \\rightarrow 3'$ direction (requires only one RNA primer).
- **Lagging Strand:** Synthesized **discontinuously** away from the replication fork as short fragments known as **Okazaki fragments** (each requiring a separate RNA primer)."""
    },
    11: {
        "title": "Okazaki Fragment Processing & DNA Ligase",
        "explanation": """Discontinuous Okazaki fragments must be joined into an unbroken covalent strand:

### Maturation of the Lagging Strand
1. **DNA Polymerase I:** Excises the upstream RNA primers and fills the resulting gaps with complementary deoxyribonucleotides.
2. **DNA Ligase:** Catalyzes the formation of final **phosphodiester bonds** between adjacent fragments, sealing the sugar-phosphate backbone.
3. **High-Fidelity Proofreading:** DNA polymerase possesses $3' \\rightarrow 5'$ exonuclease activity that instantly removes mispaired nucleotides, ensuring replication error rates remain below 1 in $10^9$ bases."""
    },
    12: {
        "title": "Overview of Transcription: DNA to RNA",
        "explanation": """**Transcription** is the enzymatic synthesis of an RNA transcript complementary to a specific DNA template:

### Key Differences from DNA
- Uses ribose sugar instead of deoxyribose.
- Incorporates **Uracil ($U$)** instead of Thymine ($T$), which pairs with Adenine ($A$).
- Produces a single-stranded RNA transcript that can exit the nucleus for ribosomal translation."""
    },
    13: {
        "title": "RNA Polymerase & Promoter Recognition",
        "explanation": """Transcription begins at specific regulatory DNA sequences known as **promoters**:

### Initiation Complex
- **The Promoter:** Contains conserved sequence motifs (such as the eukaryotic **TATA box**) located upstream of the transcription start site.
- **Transcription Factors:** Guide and recruit **RNA Polymerase II** to the promoter to form the pre-initiation complex.
- **Unwinding:** RNA polymerase locally melts the DNA double helix without requiring a separate helicase."""
    },
    14: {
        "title": "Three Stages of Transcription",
        "explanation": """Transcription proceeds through three distinct, tightly coordinated phases:

### Transcription Cascade
1. **Initiation:** RNA polymerase binds the promoter, unwinds approximately 14 base pairs of DNA, and initiates RNA synthesis.
2. **Elongation:** RNA polymerase traverses the DNA template strand in the $3' \\rightarrow 5'$ direction, adding ribonucleotides ($A, U, G, C$) to synthesize mRNA in the $5' \\rightarrow 3'$ direction.
3. **Termination:** Upon transcribing a specific terminator sequence (or polyadenylation signal), the nascent transcript and RNA polymerase detach from the DNA."""
    },
    15: {
        "title": "Post-Transcriptional RNA Processing in Eukaryotes",
        "explanation": """Primary eukaryotic transcripts (pre-mRNA) must undergo nuclear maturation before cytosolic export:

### Three Processing Events
1. **$5'$ Capping:** Addition of a 7-methylguanosine cap to protect mRNA from exonuclease degradation and assist in ribosomal recognition.
2. **Polyadenylation ($3'$ Poly-A Tail):** Enzymatic addition of 100–250 adenine residues to the $3'$ end to stabilize the transcript and facilitate nuclear export.
3. **RNA Splicing:** Large molecular complexes called **spliceosomes** excise non-coding **introns** and ligate coding **exons** together."""
    },
    16: {
        "title": "The Triplet Genetic Code & Codons",
        "explanation": """The genetic code translates a 4-letter nucleotide alphabet into a 20-letter amino acid alphabet:

### Triplet Code Principles
- **Codons:** Consecutive sequences of three mRNA nucleotides that specify a particular amino acid.
- **64 Possible Triplet Combinations (4³ = 64):**
  - **Start Codon:** **AUG** encodes Methionine and establishes the reading frame.
  - **Stop Codons:** **UAA, UAG, and UGA** signal termination of translation and encode no amino acid.
  - **61 Sense Codons:** Direct the incorporation of the 20 standard amino acids."""
    },
    17: {
        "title": "Universal Characteristics of the Genetic Code",
        "explanation": """The genetic code possesses three fundamental evolutionary properties:

### Core Properties
- **Universal:** Shared across virtually all living organisms—from bacteria to humans—providing profound evidence of common ancestry.
- **Degenerate (Redundant):** Multiple distinct codons can specify the same amino acid (e.g., Leucine is encoded by six different codons), buffering against point mutations.
- **Non-Overlapping & Comma-less:** Codons are read consecutively in groups of three without skipping or sharing nucleotides."""
    },
    18: {
        "title": "Overview of Translation: RNA to Polypeptide",
        "explanation": """**Translation** is the complex molecular process wherein ribosomes synthesize a polypeptide chain dictated by mRNA codons:

### Required Translational Machinery
- **Messenger RNA (mRNA):** Carries the genetic transcript from the nucleus.
- **Ribosomes:** Catalytic molecular machines composed of ribosomal RNA (rRNA) and proteins.
- **Transfer RNA (tRNA):** Adaptor molecules that physically bridge codons to corresponding amino acids."""
    },
    19: {
        "title": "Transfer RNA (tRNA) Adaptor Architecture",
        "explanation": """tRNA molecules act as the physical translators between nucleotide language and amino acid language:

### Structural Domains
- **Cloverleaf Secondary Structure:** Folds into an L-shaped three-dimensional tertiary conformation.
- **Anticodon Loop:** A triplet nucleotide sequence complementary and antiparallel to a specific mRNA codon.
- **$3'$ Amino Acid Attachment Site (CCA-terminus):** Covalently binds the specific amino acid matching the anticodon."""
    },
    20: {
        "title": "Aminoacyl-tRNA Synthetase: Charging tRNA",
        "explanation": """High translational fidelity depends on the precision of **aminoacyl-tRNA synthetases**:

### The "Second Genetic Code"
- **Enzymatic Activation:** Specific synthetase enzymes hydrolyze ATP to attach the correct amino acid to its cognate tRNA.
- **Charged (Aminoacyl) tRNA:** Once attached, the aminoacyl-tRNA delivers its amino acid to the active ribosome.
- **Proofreading:** Synthetases possess editing pockets that hydrolyze incorrectly attached amino acids prior to release."""
    },
    21: {
        "title": "Ribosome Architecture & Binding Sites",
        "explanation": """Eukaryotic (80S) and prokaryotic (70S) ribosomes provide coordinated reaction chambers for peptide synthesis:

### Three Ribosomal tRNA Binding Sites
- **A Site (Aminoacyl):** Binds the incoming charged aminoacyl-tRNA bearing the next amino acid in the sequence.
- **P Site (Peptidyl):** Holds the tRNA carrying the growing nascent polypeptide chain.
- **E Site (Exit):** Binds the deacylated, empty tRNA prior to its release back into the cytosol."""
    },
    22: {
        "title": "Translation Initiation Cascade",
        "explanation": """Initiation assembles the complete ribosomal complex at the proper start codon:

### Sequential Steps
1. The small ribosomal subunit binds initiation factors and scans the $5'$ mRNA cap until it locates the **AUG start codon**.
2. Initiator tRNA carrying Methionine (Met) binds the AUG codon in the **P site**.
3. The large ribosomal subunit docks onto the small subunit, hydrolyzing GTP to form the translationally competent $80S$ initiation complex."""
    },
    23: {
        "title": "Translation Elongation Cycle",
        "explanation": """Polypeptide elongation occurs as a repeating three-step mechanical cycle:

### The Elongation Cycle
1. **Codon Recognition:** An incoming aminoacyl-tRNA matches its anticodon to the mRNA codon occupying the **A site**.
2. **Peptide Bond Formation:** The ribosome's **peptidyl transferase** transfers the growing polypeptide from the P site tRNA to the amino acid on the A site tRNA.
3. **Translocation:** The ribosome shifts three nucleotides along the mRNA toward the $3'$ end; the empty tRNA moves to the **E site** and exits, while the peptidyl-tRNA moves from the A to the **P site**."""
    },
    24: {
        "title": "Peptidyl Transferase: Catalytic Ribozyme Action",
        "explanation": """Peptide bond synthesis is catalyzed not by ribosomal proteins, but by ribosomal RNA itself:

### Ribozyme Activity
- The catalytic core of the large ribosomal subunit is composed of **28S rRNA** (in eukaryotes), acting as a **ribozyme**.
- Catalyzes a condensation reaction between the amino group of the A-site amino acid and the carboxyl terminus of the P-site peptidyl chain, forming a stable covalent **peptide bond**."""
    },
    25: {
        "title": "Translation Termination & Polypeptide Release",
        "explanation": """Termination halts synthesis when a stop codon reaches the ribosomal A site:

### Termination Cascade
- **Stop Codons:** When **UAA, UAG, or UGA** enters the A site, no normal tRNA can pair with it.
- **Release Factors (RF):** A protein release factor binds directly to the stop codon.
- **Hydrolytic Cleavage:** The release factor stimulates peptidyl transferase to add a water molecule instead of an amino acid, cleaving the finished polypeptide from the P-site tRNA.
- **Complex Disassembly:** The ribosomal subunits, mRNA transcript, and empty tRNAs dissociate."""
    },
    26: {
        "title": "Polyribosomes (Polysomes) & High-Yield Translation",
        "explanation": """Cells maximize protein production efficiency through simultaneous translation:

### Polysome Architecture
- A single mature mRNA transcript is translated simultaneously by **multiple trailing ribosomes**, spaced approximately 80 nucleotides apart like beads on a string.
- As soon as the first ribosome moves past the start codon, another ribosome docks, enabling the rapid synthesis of hundreds of identical protein copies from a single mRNA molecule."""
    },
    27: {
        "title": "From Gene to Functional Protein: Post-Translational Folding",
        "explanation": """Linear polypeptide synthesis is only the initial step in producing a functional protein:

### Maturation & Folding
- **Chaperone Proteins:** Assist nascent polypeptides to fold into their thermodynamically stable secondary and tertiary conformations.
- **Post-Translational Modifications:** Phosphorylation, glycosylation, lipidation, or proteolytic cleavage (e.g., proinsulin to insulin) activate or direct the protein to its cellular destination."""
    }
}
