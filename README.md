COSC2671 Social Media and Network Analytics
Assignment 2 - User Perceptions of Apple and Samsung Ecosystems
Authors: Ngoc Anh Thu Nguyen, Ritik Kadwane

Recommended Python version: Python 3.10+
Tested using Jupyter Notebook 

================================================================
FULL DATASET ACCESS
================================================================

Representative dataset samples are included in this submission package in accordance with the assignment size requirements.
The complete Reddit and YouTube datasets, along with the full project repository, notebook versions, and supporting files, 
are available through the GitHub repository below:

https://github.com/ritikkadwane/Assignment-2_Social-Media-and-Network-Analysis.git


================================================================
REQUIRED PACKAGES - install these dependencies before running
================================================================

pip install vaderSentiment
pip install gensim
pip install pyLDAvis
pip install python-louvain
pip install networkx
pip install scikit-learn
pip install nltk
pip install wordcloud
pip install seaborn
pip install matplotlib
pip install pandas
pip install numpy

Or install all at once:

pip install vaderSentiment gensim pyLDAvis python-louvain networkx scikit-learn nltk wordcloud seaborn matplotlib pandas numpy

================================================================
NLTK DOWNLOADS - run once inside the notebook (already in code)
================================================================

import nltk
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

================================================================
FILE STRUCTURE - required files in the same folder as notebook
================================================================

reddit_data.json          - Reddit dataset collected via Arctic Shift API
youtube_data.json         - YouTube dataset collected via YouTube Data API v3
s3912314_s4068547_PG_Group12.ipynb  - Main analysis notebook

The notebook automatically generates optional cache and model files
during the first execution to reduce runtime in later runs.
models/                 - Folder containing cached LDA model files
  iphone_lda.model        - Saved iPhone LDA topic model
  samsung_lda.model       - Saved Samsung LDA topic model
  iphone_dict.dict        - iPhone Gensim dictionary
  samsung_dict.dict       - Samsung Gensim dictionary
  iphone_corpus.pkl       - iPhone bag of words corpus
  samsung_corpus.pkl      - Samsung bag of words corpus
  iphone_coherence.pkl    - iPhone coherence scores
  samsung_coherence.pkl   - Samsung coherence scores

(optional cache files generated after first execution)

================================================================
ESTIMATED RUNTIME
================================================================

Section 1-4  (Loading, Preprocessing, EDA)     : 1-2 minutes
Section 5    (VADER Sentiment Analysis)         : 2-3 minutes
Section 6    (LDA Topic Modelling)
  - First run, training from scratch            : 25-40 minutes
  - Subsequent runs, loading from cache         : under 1 minute
Section 7    (Network Construction)             : 1-2 minutes
Section 8    (Centrality - betweenness k=500)   : 3-5 minutes
Section 9    (Louvain Community Detection)      : 1-2 minutes
Section 10   (Diffusion - IC 100 simulations)   : 2-4 minutes
Section 11-12 (Comparison, Summary)             : under 1 minute

Full execution from scratch may take approximately 40-55 minutes
depending on hardware and internet speed.

Total cached run : approximately 15-20 minutes

If runtime is a concern, pre-generated outputs and visualisations
are already included within the notebook execution results.

================================================================
NOTES
================================================================

- LDA models are saved automatically after first training run.
  Delete the .model and .pkl files only if you want to retrain.

- If you see a model incompatibility error on load, the notebook
  will automatically retrain the models from scratch.

- Run cells in order from top to bottom. Do not skip sections
  as later sections depend on variables from earlier ones.

- The results summary cell at the end (Section 12) requires all
  previous sections to have run successfully.

- Data was collected on 21 May 2026.
  Reddit  : Arctic Shift API
  YouTube : YouTube Data API v3

================================================================
DATA SOURCES AND API CREDITS
================================================================

Reddit Data
  Arctic Shift API by Arthur Heitmann
  Used to collect Reddit posts and comments from subreddits
  including r/iphone, r/Samsung, r/Android, r/apple, r/Smartphones
  Source: https://github.com/ArthurHeitmann/arctic_shift

YouTube Data
  YouTube Data API v3 by Google
  Used to collect video comments from Samsung vs iPhone
  comparison videos on YouTube
  Source: https://developers.google.com/youtube/v3
  Terms:  https://developers.google.com/youtube/terms/api-services-terms-of-service

================================================================
KEY REFERENCES USED DURING DEVELOPMENT
================================================================

Sentiment Analysis
  Hutto, C.J. and Gilbert, E. (2014). VADER: A Parsimonious
  Rule-based Model for Sentiment Analysis of Social Media Text.
  ICWSM. https://github.com/cjhutto/vaderSentiment

Topic Modelling
  Blei, D., Ng, A. and Jordan, M. (2003). Latent Dirichlet
  Allocation. Journal of Machine Learning Research, 3, 993-1022.
  Gensim LDA documentation: https://radimrehurek.com/gensim/

Community Detection
  Blondel, V. et al. (2008). Fast unfolding of communities in
  large networks. Journal of Statistical Mechanics.
  python-louvain: https://python-louvain.readthedocs.io/

Information Diffusion
  Kempe, D., Kleinberg, J. and Tardos, E. (2003). Maximizing
  the spread of influence through a social network. ACM SIGKDD.

Network Analysis
  NetworkX documentation: https://networkx.org/documentation/
  Stack Overflow - NetworkX community, various threads on
  centrality, betweenness, and PageRank implementation:
  https://stackoverflow.com/questions/tagged/networkx

General Python and Data Science
  Stack Overflow - pandas, matplotlib, seaborn, scikit-learn
  https://stackoverflow.com/questions/tagged/pandas
  https://stackoverflow.com/questions/tagged/matplotlib
  https://stackoverflow.com/questions/tagged/scikit-learn
  Towards Data Science - LDA topic modelling tutorials
  https://towardsdatascience.com
  Real Python - Python data processing guides
  https://realpython.com

================================================================
AI TOOLS ACKNOWLEDGEMENT
================================================================

AI assistants were used during the development of this project
in the following ways:

Claude (Anthropic) - claude.ai and ChatGPT (OpenAI) - chat.openai.com
  Used to assist with code debugging, markdown writing, and
  reviewing analysis interpretation. All code logic, analysis
  decisions, and conclusions were developed and verified by
  the team. Claude was not used to generate raw analysis
  outputs or fabricate results.


All AI-assisted content was reviewed, verified, and adapted
by the authors. AI tools were used as a support resource,
not as a substitute for the team's own analytical work.
This is disclosed in accordance with RMIT academic integrity
guidelines.

================================================================
