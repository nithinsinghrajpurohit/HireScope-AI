"""
Comprehensive skills taxonomy with 500+ skills organized by category.
Each skill has aliases, category, and optional related skills.
"""

SKILLS_DB = {
    # ═══════════════════════════════════════════
    # PROGRAMMING LANGUAGES
    # ═══════════════════════════════════════════
    "python": {
        "category": "Programming",
        "aliases": ["python3", "python2", "py", "cpython"],
        "related": ["django", "flask", "fastapi", "numpy", "pandas"],
    },
    "java": {
        "category": "Programming",
        "aliases": ["java8", "java11", "java17", "jdk", "j2ee"],
        "related": ["spring", "maven", "gradle", "hibernate"],
    },
    "javascript": {
        "category": "Programming",
        "aliases": ["js", "ecmascript", "es6", "es2015", "vanilla js"],
        "related": ["react", "node.js", "vue", "angular"],
    },
    "typescript": {
        "category": "Programming",
        "aliases": ["ts"],
        "related": ["javascript", "angular", "react"],
    },
    "c++": {
        "category": "Programming",
        "aliases": ["cpp", "c plus plus", "cplusplus", "c++11", "c++14", "c++17"],
        "related": ["c", "cmake", "boost"],
    },
    "c": {
        "category": "Programming",
        "aliases": ["c language", "ansi c", "c99", "c11"],
        "related": ["c++", "embedded systems"],
    },
    "c#": {
        "category": "Programming",
        "aliases": ["csharp", "c sharp", "dotnet"],
        "related": [".net", "asp.net", "unity"],
    },
    "go": {
        "category": "Programming",
        "aliases": ["golang", "go language"],
        "related": ["docker", "kubernetes", "microservices"],
    },
    "rust": {
        "category": "Programming",
        "aliases": ["rust-lang", "rustlang"],
        "related": ["systems programming", "webassembly"],
    },
    "ruby": {
        "category": "Programming",
        "aliases": ["rb"],
        "related": ["ruby on rails", "sinatra"],
    },
    "php": {
        "category": "Programming",
        "aliases": ["php7", "php8"],
        "related": ["laravel", "symfony", "wordpress"],
    },
    "swift": {
        "category": "Programming",
        "aliases": ["swift5"],
        "related": ["ios", "xcode", "swiftui"],
    },
    "kotlin": {
        "category": "Programming",
        "aliases": ["kt"],
        "related": ["android", "jetpack compose", "spring"],
    },
    "r": {
        "category": "Programming",
        "aliases": ["r language", "r programming", "rstudio", "r-project"],
        "related": ["ggplot2", "shiny", "tidyverse", "statistics"],
    },
    "scala": {
        "category": "Programming",
        "aliases": [],
        "related": ["spark", "akka", "play framework"],
    },
    "perl": {
        "category": "Programming",
        "aliases": ["perl5", "perl6"],
        "related": ["regex", "scripting"],
    },
    "matlab": {
        "category": "Programming",
        "aliases": ["mat lab"],
        "related": ["simulink", "signal processing"],
    },
    "sql": {
        "category": "Programming",
        "aliases": ["structured query language", "t-sql", "pl/sql", "plsql"],
        "related": ["mysql", "postgresql", "oracle", "sql server"],
    },
    "bash": {
        "category": "Programming",
        "aliases": ["shell", "shell scripting", "bash scripting", "sh"],
        "related": ["linux", "unix", "command line"],
    },
    "powershell": {
        "category": "Programming",
        "aliases": ["ps1", "pwsh"],
        "related": ["windows", "automation", "scripting"],
    },
    "dart": {
        "category": "Programming",
        "aliases": [],
        "related": ["flutter", "mobile development"],
    },
    "lua": {
        "category": "Programming",
        "aliases": [],
        "related": ["game development", "scripting"],
    },
    "haskell": {
        "category": "Programming",
        "aliases": [],
        "related": ["functional programming"],
    },
    "elixir": {
        "category": "Programming",
        "aliases": [],
        "related": ["phoenix", "erlang"],
    },

    # ═══════════════════════════════════════════
    # FRAMEWORKS & LIBRARIES
    # ═══════════════════════════════════════════
    "react": {
        "category": "Frameworks",
        "aliases": ["reactjs", "react.js", "react js"],
        "related": ["javascript", "redux", "next.js"],
    },
    "angular": {
        "category": "Frameworks",
        "aliases": ["angularjs", "angular.js", "angular 2+"],
        "related": ["typescript", "rxjs"],
    },
    "vue": {
        "category": "Frameworks",
        "aliases": ["vuejs", "vue.js", "vue js", "vue 3"],
        "related": ["javascript", "nuxt.js", "vuex"],
    },
    "next.js": {
        "category": "Frameworks",
        "aliases": ["nextjs", "next js"],
        "related": ["react", "vercel"],
    },
    "node.js": {
        "category": "Frameworks",
        "aliases": ["nodejs", "node js", "node"],
        "related": ["express", "javascript", "npm"],
    },
    "express": {
        "category": "Frameworks",
        "aliases": ["expressjs", "express.js"],
        "related": ["node.js", "rest api"],
    },
    "django": {
        "category": "Frameworks",
        "aliases": ["django rest framework", "drf"],
        "related": ["python", "web development"],
    },
    "flask": {
        "category": "Frameworks",
        "aliases": ["flask api"],
        "related": ["python", "web development", "rest api"],
    },
    "fastapi": {
        "category": "Frameworks",
        "aliases": ["fast api"],
        "related": ["python", "async", "rest api"],
    },
    "spring": {
        "category": "Frameworks",
        "aliases": ["spring boot", "spring framework", "spring mvc"],
        "related": ["java", "microservices"],
    },
    "ruby on rails": {
        "category": "Frameworks",
        "aliases": ["rails", "ror"],
        "related": ["ruby", "web development"],
    },
    "laravel": {
        "category": "Frameworks",
        "aliases": [],
        "related": ["php", "web development"],
    },
    ".net": {
        "category": "Frameworks",
        "aliases": ["dotnet", "dot net", ".net core", "asp.net"],
        "related": ["c#", "azure"],
    },
    "flutter": {
        "category": "Frameworks",
        "aliases": [],
        "related": ["dart", "mobile development"],
    },
    "react native": {
        "category": "Frameworks",
        "aliases": ["react-native", "rn"],
        "related": ["react", "mobile development"],
    },
    "svelte": {
        "category": "Frameworks",
        "aliases": ["sveltejs", "sveltekit"],
        "related": ["javascript", "web development"],
    },
    "tailwind css": {
        "category": "Frameworks",
        "aliases": ["tailwindcss", "tailwind"],
        "related": ["css", "web development"],
    },
    "bootstrap": {
        "category": "Frameworks",
        "aliases": ["bootstrap5", "bootstrap 5"],
        "related": ["css", "web development"],
    },
    "jquery": {
        "category": "Frameworks",
        "aliases": ["jquery.js"],
        "related": ["javascript", "dom manipulation"],
    },

    # ═══════════════════════════════════════════
    # DATA SCIENCE & ML
    # ═══════════════════════════════════════════
    "machine learning": {
        "category": "Data Science",
        "aliases": ["ml", "machine-learning"],
        "related": ["deep learning", "scikit-learn", "supervised learning"],
    },
    "deep learning": {
        "category": "Data Science",
        "aliases": ["dl", "deep-learning"],
        "related": ["neural networks", "tensorflow", "pytorch"],
    },
    "artificial intelligence": {
        "category": "Data Science",
        "aliases": ["ai", "a.i."],
        "related": ["machine learning", "nlp", "computer vision"],
    },
    "natural language processing": {
        "category": "Data Science",
        "aliases": ["nlp", "text mining", "text analytics"],
        "related": ["transformers", "bert", "spacy"],
    },
    "computer vision": {
        "category": "Data Science",
        "aliases": ["cv", "image processing", "image recognition"],
        "related": ["opencv", "cnn", "yolo"],
    },
    "data analysis": {
        "category": "Data Science",
        "aliases": ["data analytics", "data analyst"],
        "related": ["pandas", "excel", "sql", "visualization"],
    },
    "data engineering": {
        "category": "Data Science",
        "aliases": ["data pipeline", "etl"],
        "related": ["spark", "airflow", "kafka"],
    },
    "data visualization": {
        "category": "Data Science",
        "aliases": ["data viz", "dataviz"],
        "related": ["matplotlib", "tableau", "power bi", "plotly"],
    },
    "statistics": {
        "category": "Data Science",
        "aliases": ["statistical analysis", "stats", "statistical modeling"],
        "related": ["r", "hypothesis testing", "regression"],
    },
    "tensorflow": {
        "category": "Data Science",
        "aliases": ["tf", "tensorflow2", "tf2"],
        "related": ["keras", "deep learning", "neural networks"],
    },
    "pytorch": {
        "category": "Data Science",
        "aliases": ["torch"],
        "related": ["deep learning", "neural networks"],
    },
    "keras": {
        "category": "Data Science",
        "aliases": [],
        "related": ["tensorflow", "deep learning"],
    },
    "scikit-learn": {
        "category": "Data Science",
        "aliases": ["sklearn", "scikit learn"],
        "related": ["machine learning", "python"],
    },
    "pandas": {
        "category": "Data Science",
        "aliases": [],
        "related": ["python", "data analysis", "numpy"],
    },
    "numpy": {
        "category": "Data Science",
        "aliases": [],
        "related": ["python", "scientific computing"],
    },
    "scipy": {
        "category": "Data Science",
        "aliases": [],
        "related": ["python", "scientific computing", "numpy"],
    },
    "matplotlib": {
        "category": "Data Science",
        "aliases": ["mpl"],
        "related": ["python", "data visualization"],
    },
    "plotly": {
        "category": "Data Science",
        "aliases": [],
        "related": ["data visualization", "dash"],
    },
    "tableau": {
        "category": "Data Science",
        "aliases": [],
        "related": ["data visualization", "business intelligence"],
    },
    "power bi": {
        "category": "Data Science",
        "aliases": ["powerbi", "power-bi"],
        "related": ["data visualization", "business intelligence", "microsoft"],
    },
    "spark": {
        "category": "Data Science",
        "aliases": ["apache spark", "pyspark"],
        "related": ["big data", "hadoop", "data engineering"],
    },
    "hadoop": {
        "category": "Data Science",
        "aliases": ["apache hadoop", "hdfs", "mapreduce"],
        "related": ["big data", "spark"],
    },
    "big data": {
        "category": "Data Science",
        "aliases": ["bigdata"],
        "related": ["spark", "hadoop", "kafka"],
    },
    "neural networks": {
        "category": "Data Science",
        "aliases": ["nn", "ann", "artificial neural network"],
        "related": ["deep learning", "cnn", "rnn"],
    },
    "convolutional neural network": {
        "category": "Data Science",
        "aliases": ["cnn", "convnet"],
        "related": ["computer vision", "deep learning"],
    },
    "recurrent neural network": {
        "category": "Data Science",
        "aliases": ["rnn", "lstm", "gru"],
        "related": ["nlp", "deep learning", "time series"],
    },
    "transformers": {
        "category": "Data Science",
        "aliases": ["transformer model", "attention mechanism"],
        "related": ["bert", "gpt", "nlp"],
    },
    "bert": {
        "category": "Data Science",
        "aliases": [],
        "related": ["nlp", "transformers", "hugging face"],
    },
    "gpt": {
        "category": "Data Science",
        "aliases": ["gpt-3", "gpt-4", "chatgpt", "openai"],
        "related": ["nlp", "llm", "transformers"],
    },
    "large language models": {
        "category": "Data Science",
        "aliases": ["llm", "llms"],
        "related": ["gpt", "bert", "nlp", "transformers"],
    },
    "reinforcement learning": {
        "category": "Data Science",
        "aliases": ["rl"],
        "related": ["machine learning", "deep learning"],
    },
    "generative ai": {
        "category": "Data Science",
        "aliases": ["gen ai", "genai"],
        "related": ["llm", "gpt", "stable diffusion"],
    },
    "mlops": {
        "category": "Data Science",
        "aliases": ["ml ops", "machine learning operations"],
        "related": ["mlflow", "kubeflow", "model deployment"],
    },
    "feature engineering": {
        "category": "Data Science",
        "aliases": [],
        "related": ["machine learning", "data preprocessing"],
    },
    "model deployment": {
        "category": "Data Science",
        "aliases": ["ml deployment", "model serving"],
        "related": ["mlops", "docker", "kubernetes"],
    },
    "time series analysis": {
        "category": "Data Science",
        "aliases": ["time series", "time-series", "forecasting"],
        "related": ["arima", "prophet", "statistics"],
    },
    "recommendation systems": {
        "category": "Data Science",
        "aliases": ["recommender systems", "collaborative filtering"],
        "related": ["machine learning", "matrix factorization"],
    },
    "a/b testing": {
        "category": "Data Science",
        "aliases": ["ab testing", "split testing"],
        "related": ["statistics", "experimentation"],
    },
    "opencv": {
        "category": "Data Science",
        "aliases": ["open cv", "cv2"],
        "related": ["computer vision", "image processing"],
    },
    "spacy": {
        "category": "Data Science",
        "aliases": [],
        "related": ["nlp", "python"],
    },
    "hugging face": {
        "category": "Data Science",
        "aliases": ["huggingface", "hf"],
        "related": ["transformers", "nlp", "bert"],
    },
    "xgboost": {
        "category": "Data Science",
        "aliases": [],
        "related": ["machine learning", "gradient boosting"],
    },
    "lightgbm": {
        "category": "Data Science",
        "aliases": [],
        "related": ["machine learning", "gradient boosting"],
    },
    "random forest": {
        "category": "Data Science",
        "aliases": [],
        "related": ["machine learning", "ensemble methods"],
    },

    # ═══════════════════════════════════════════
    # DATABASES
    # ═══════════════════════════════════════════
    "mysql": {
        "category": "Databases",
        "aliases": ["my sql"],
        "related": ["sql", "relational database"],
    },
    "postgresql": {
        "category": "Databases",
        "aliases": ["postgres", "psql", "pg"],
        "related": ["sql", "relational database"],
    },
    "mongodb": {
        "category": "Databases",
        "aliases": ["mongo"],
        "related": ["nosql", "document database"],
    },
    "redis": {
        "category": "Databases",
        "aliases": [],
        "related": ["caching", "in-memory database"],
    },
    "elasticsearch": {
        "category": "Databases",
        "aliases": ["elastic search", "elastic", "es"],
        "related": ["search engine", "logging", "elk"],
    },
    "cassandra": {
        "category": "Databases",
        "aliases": ["apache cassandra"],
        "related": ["nosql", "distributed database"],
    },
    "dynamodb": {
        "category": "Databases",
        "aliases": ["dynamo db"],
        "related": ["aws", "nosql"],
    },
    "oracle": {
        "category": "Databases",
        "aliases": ["oracle db", "oracle database"],
        "related": ["sql", "pl/sql"],
    },
    "sql server": {
        "category": "Databases",
        "aliases": ["mssql", "microsoft sql server", "ms sql"],
        "related": ["sql", "t-sql", "microsoft"],
    },
    "sqlite": {
        "category": "Databases",
        "aliases": [],
        "related": ["sql", "embedded database"],
    },
    "neo4j": {
        "category": "Databases",
        "aliases": [],
        "related": ["graph database", "cypher"],
    },
    "firebase": {
        "category": "Databases",
        "aliases": ["firestore"],
        "related": ["google cloud", "nosql", "realtime database"],
    },
    "supabase": {
        "category": "Databases",
        "aliases": [],
        "related": ["postgresql", "backend as a service"],
    },

    # ═══════════════════════════════════════════
    # CLOUD & INFRASTRUCTURE
    # ═══════════════════════════════════════════
    "aws": {
        "category": "Cloud",
        "aliases": ["amazon web services", "amazon aws"],
        "related": ["ec2", "s3", "lambda", "cloud computing"],
    },
    "azure": {
        "category": "Cloud",
        "aliases": ["microsoft azure", "azure cloud"],
        "related": ["cloud computing", "microsoft"],
    },
    "google cloud": {
        "category": "Cloud",
        "aliases": ["gcp", "google cloud platform"],
        "related": ["cloud computing", "bigquery"],
    },
    "docker": {
        "category": "Cloud",
        "aliases": ["containerization", "docker compose"],
        "related": ["kubernetes", "devops", "containers"],
    },
    "kubernetes": {
        "category": "Cloud",
        "aliases": ["k8s", "kube"],
        "related": ["docker", "container orchestration", "devops"],
    },
    "terraform": {
        "category": "Cloud",
        "aliases": [],
        "related": ["infrastructure as code", "devops", "cloud"],
    },
    "ansible": {
        "category": "Cloud",
        "aliases": [],
        "related": ["configuration management", "devops", "automation"],
    },
    "jenkins": {
        "category": "Cloud",
        "aliases": [],
        "related": ["ci/cd", "devops", "automation"],
    },
    "ci/cd": {
        "category": "Cloud",
        "aliases": ["cicd", "ci cd", "continuous integration", "continuous deployment"],
        "related": ["jenkins", "github actions", "devops"],
    },
    "github actions": {
        "category": "Cloud",
        "aliases": ["gh actions"],
        "related": ["ci/cd", "github", "devops"],
    },
    "serverless": {
        "category": "Cloud",
        "aliases": ["faas", "function as a service"],
        "related": ["aws lambda", "azure functions", "cloud"],
    },
    "microservices": {
        "category": "Cloud",
        "aliases": ["micro services", "microservice architecture"],
        "related": ["docker", "kubernetes", "api gateway"],
    },
    "linux": {
        "category": "Cloud",
        "aliases": ["linux administration", "ubuntu", "centos", "debian"],
        "related": ["bash", "unix", "system administration"],
    },
    "nginx": {
        "category": "Cloud",
        "aliases": [],
        "related": ["web server", "reverse proxy", "load balancing"],
    },
    "apache kafka": {
        "category": "Cloud",
        "aliases": ["kafka"],
        "related": ["event streaming", "message queue", "data engineering"],
    },
    "rabbitmq": {
        "category": "Cloud",
        "aliases": ["rabbit mq"],
        "related": ["message queue", "microservices"],
    },

    # ═══════════════════════════════════════════
    # TOOLS & PLATFORMS
    # ═══════════════════════════════════════════
    "git": {
        "category": "Tools",
        "aliases": ["git version control"],
        "related": ["github", "gitlab", "bitbucket"],
    },
    "github": {
        "category": "Tools",
        "aliases": [],
        "related": ["git", "version control", "ci/cd"],
    },
    "gitlab": {
        "category": "Tools",
        "aliases": [],
        "related": ["git", "version control", "ci/cd"],
    },
    "jira": {
        "category": "Tools",
        "aliases": [],
        "related": ["agile", "project management", "atlassian"],
    },
    "confluence": {
        "category": "Tools",
        "aliases": [],
        "related": ["documentation", "atlassian"],
    },
    "slack": {
        "category": "Tools",
        "aliases": [],
        "related": ["communication", "team collaboration"],
    },
    "vs code": {
        "category": "Tools",
        "aliases": ["visual studio code", "vscode"],
        "related": ["ide", "development"],
    },
    "postman": {
        "category": "Tools",
        "aliases": [],
        "related": ["api testing", "rest api"],
    },
    "figma": {
        "category": "Tools",
        "aliases": [],
        "related": ["ui/ux design", "prototyping"],
    },
    "jupyter": {
        "category": "Tools",
        "aliases": ["jupyter notebook", "jupyter lab", "ipython"],
        "related": ["python", "data science"],
    },
    "excel": {
        "category": "Tools",
        "aliases": ["microsoft excel", "ms excel", "spreadsheet"],
        "related": ["data analysis", "vba"],
    },
    "swagger": {
        "category": "Tools",
        "aliases": ["openapi", "swagger ui"],
        "related": ["api documentation", "rest api"],
    },
    "grafana": {
        "category": "Tools",
        "aliases": [],
        "related": ["monitoring", "dashboards", "prometheus"],
    },
    "airflow": {
        "category": "Tools",
        "aliases": ["apache airflow"],
        "related": ["data engineering", "workflow orchestration"],
    },
    "mlflow": {
        "category": "Tools",
        "aliases": [],
        "related": ["mlops", "experiment tracking"],
    },

    # ═══════════════════════════════════════════
    # WEB DEVELOPMENT
    # ═══════════════════════════════════════════
    "html": {
        "category": "Web Development",
        "aliases": ["html5"],
        "related": ["css", "javascript", "web development"],
    },
    "css": {
        "category": "Web Development",
        "aliases": ["css3", "cascading style sheets"],
        "related": ["html", "sass", "less"],
    },
    "sass": {
        "category": "Web Development",
        "aliases": ["scss"],
        "related": ["css", "web development"],
    },
    "rest api": {
        "category": "Web Development",
        "aliases": ["restful", "rest", "restful api", "restful web services"],
        "related": ["http", "json", "api design"],
    },
    "graphql": {
        "category": "Web Development",
        "aliases": ["graph ql"],
        "related": ["api", "apollo"],
    },
    "websockets": {
        "category": "Web Development",
        "aliases": ["web sockets", "ws", "socket.io"],
        "related": ["real-time", "networking"],
    },
    "webpack": {
        "category": "Web Development",
        "aliases": [],
        "related": ["javascript", "bundling", "module bundler"],
    },
    "responsive design": {
        "category": "Web Development",
        "aliases": ["responsive web design", "rwd", "mobile-first"],
        "related": ["css", "media queries", "web development"],
    },
    "seo": {
        "category": "Web Development",
        "aliases": ["search engine optimization"],
        "related": ["web development", "marketing"],
    },
    "oauth": {
        "category": "Web Development",
        "aliases": ["oauth2", "oauth 2.0"],
        "related": ["authentication", "security"],
    },
    "jwt": {
        "category": "Web Development",
        "aliases": ["json web token"],
        "related": ["authentication", "security"],
    },

    # ═══════════════════════════════════════════
    # DEVOPS
    # ═══════════════════════════════════════════
    "devops": {
        "category": "DevOps",
        "aliases": ["dev ops"],
        "related": ["ci/cd", "docker", "kubernetes", "automation"],
    },
    "agile": {
        "category": "DevOps",
        "aliases": ["agile methodology", "agile development", "scrum master"],
        "related": ["scrum", "kanban", "sprint"],
    },
    "scrum": {
        "category": "DevOps",
        "aliases": [],
        "related": ["agile", "sprint", "kanban"],
    },
    "monitoring": {
        "category": "DevOps",
        "aliases": ["application monitoring", "system monitoring"],
        "related": ["prometheus", "grafana", "datadog"],
    },
    "prometheus": {
        "category": "DevOps",
        "aliases": [],
        "related": ["monitoring", "grafana", "alerting"],
    },
    "testing": {
        "category": "DevOps",
        "aliases": ["unit testing", "integration testing", "test automation"],
        "related": ["pytest", "jest", "selenium"],
    },
    "selenium": {
        "category": "DevOps",
        "aliases": [],
        "related": ["testing", "web automation", "qa"],
    },
    "pytest": {
        "category": "DevOps",
        "aliases": [],
        "related": ["python", "testing", "unit testing"],
    },

    # ═══════════════════════════════════════════
    # MOBILE DEVELOPMENT
    # ═══════════════════════════════════════════
    "ios": {
        "category": "Mobile",
        "aliases": ["ios development"],
        "related": ["swift", "xcode", "swiftui"],
    },
    "android": {
        "category": "Mobile",
        "aliases": ["android development"],
        "related": ["kotlin", "java", "jetpack"],
    },
    "mobile development": {
        "category": "Mobile",
        "aliases": ["mobile app development", "mobile apps"],
        "related": ["flutter", "react native", "ios", "android"],
    },

    # ═══════════════════════════════════════════
    # SOFT SKILLS
    # ═══════════════════════════════════════════
    "leadership": {
        "category": "Soft Skills",
        "aliases": ["team leadership", "team lead", "tech lead"],
        "related": ["management", "mentoring"],
    },
    "communication": {
        "category": "Soft Skills",
        "aliases": ["written communication", "verbal communication", "presentation skills"],
        "related": ["teamwork", "collaboration"],
    },
    "problem solving": {
        "category": "Soft Skills",
        "aliases": ["problem-solving", "analytical thinking", "critical thinking"],
        "related": ["debugging", "analysis"],
    },
    "teamwork": {
        "category": "Soft Skills",
        "aliases": ["team player", "collaboration", "cross-functional"],
        "related": ["communication", "agile"],
    },
    "project management": {
        "category": "Soft Skills",
        "aliases": ["project planning", "program management"],
        "related": ["agile", "scrum", "jira"],
    },
    "mentoring": {
        "category": "Soft Skills",
        "aliases": ["coaching", "training", "onboarding"],
        "related": ["leadership", "knowledge sharing"],
    },
    "time management": {
        "category": "Soft Skills",
        "aliases": ["prioritization", "multitasking"],
        "related": ["productivity", "organization"],
    },
    "public speaking": {
        "category": "Soft Skills",
        "aliases": ["presentations", "tech talks"],
        "related": ["communication", "leadership"],
    },
    "technical writing": {
        "category": "Soft Skills",
        "aliases": ["documentation", "tech writing"],
        "related": ["communication", "confluence"],
    },
    "research": {
        "category": "Soft Skills",
        "aliases": ["research skills", "literature review"],
        "related": ["analysis", "academia"],
    },

    # ═══════════════════════════════════════════
    # SECURITY
    # ═══════════════════════════════════════════
    "cybersecurity": {
        "category": "Tools",
        "aliases": ["cyber security", "information security", "infosec"],
        "related": ["penetration testing", "security"],
    },
    "penetration testing": {
        "category": "Tools",
        "aliases": ["pen testing", "ethical hacking"],
        "related": ["cybersecurity", "security"],
    },
    "encryption": {
        "category": "Tools",
        "aliases": ["cryptography", "ssl", "tls"],
        "related": ["security", "data protection"],
    },

    # ═══════════════════════════════════════════
    # DESIGN & UX
    # ═══════════════════════════════════════════
    "ui/ux design": {
        "category": "Tools",
        "aliases": ["ui design", "ux design", "user experience", "user interface"],
        "related": ["figma", "wireframing", "prototyping"],
    },
    "wireframing": {
        "category": "Tools",
        "aliases": ["wireframes"],
        "related": ["ui/ux design", "prototyping"],
    },
}


def get_all_skill_names() -> list:
    """Return a flat list of all skill names and their aliases."""
    names = []
    for skill, data in SKILLS_DB.items():
        names.append(skill)
        names.extend(data.get("aliases", []))
    return names


def get_skills_by_category() -> dict:
    """Group skills by their category."""
    categories = {}
    for skill, data in SKILLS_DB.items():
        cat = data["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)
    return categories


def get_skill_info(skill_name: str) -> dict | None:
    """Look up a skill by name or alias. Returns skill data or None."""
    skill_lower = skill_name.lower().strip()
    # Direct match
    if skill_lower in SKILLS_DB:
        return {"name": skill_lower, **SKILLS_DB[skill_lower]}
    # Alias match
    for skill, data in SKILLS_DB.items():
        if skill_lower in [a.lower() for a in data.get("aliases", [])]:
            return {"name": skill, **data}
    return None


# ───────────────────────────────────────────────────────────────────────────
# Compatibility helpers for core/skill_extractor.py
# ───────────────────────────────────────────────────────────────────────────
SKILL_ALIASES = {}
for skill, data in SKILLS_DB.items():
    for alias in data.get("aliases", []):
        SKILL_ALIASES[alias.lower()] = skill

def normalize_skill(skill_name: str) -> str | None:
    """Return the canonical skill name or None."""
    info = get_skill_info(skill_name)
    return info["name"] if info else None

def get_skill_category(skill_name: str) -> str:
    """Return the category of a skill."""
    info = get_skill_info(skill_name)
    return info["category"] if info else "Other"

def get_all_skills() -> list[str]:
    """Return a list of all canonical skill names."""
    return list(SKILLS_DB.keys())

