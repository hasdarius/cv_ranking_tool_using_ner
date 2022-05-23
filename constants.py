CONCEPTS_SCORES = {
    "intern": {
        "Seniority": 0,
        "Max Programming Language": 2,
        "Max Tool/Framework": 4,
        "Max Certification": 2,
        "Max Programming Concept": 8,
        "Max IT Specialization": 0,
        "Full Programming Language": 7,
        "Partial Programming Language": 3,
        "Full Tool/Framework": 3,
        "Partial Tool/Framework": 1.5,
        "Full Certification": 0,
        "Partial Certification": 0,
        "Full Programming Concept": 5,
        "Partial Programming Concept": 3,
        "Full IT Specialization": 0,
        "Partial IT Specialization": 0
    },
    "junior": {
        "Seniority": 1,
        "Max Programming Language": 4,
        "Max Tool/Framework": 8,
        "Max Certification": 3,
        "Max Programming Concept": 10,
        "Max IT Specialization": 2,
        "Full Programming Language": 7,
        "Partial Programming Language": 3,
        "Full Tool/Framework": 5,
        "Partial Tool/Framework": 2,
        "Full Certification": 1,
        "Partial Certification": 0.5,
        "Full Programming Concept": 3,
        "Partial Programming Concept": 1.5,
        "Full IT Specialization": 1,
        "Partial IT Specialization": 0.5
    },
    "mid": {
        "Seniority": 2,
        "Max Programming Language": 6,
        "Max Tool/Framework": 12,
        "Max Certification": 4,
        "Max Programming Concept": 12,
        "Max IT Specialization": 3,
        "Full Programming Language": 5,
        "Partial Programming Language": 2,
        "Full Tool/Framework": 7,
        "Partial Tool/Framework": 3,
        "Full Certification": 3,
        "Partial Certification": 1.5,
        "Full Programming Concept": 2,
        "Partial Programming Concept": 1,
        "Full IT Specialization": 3,
        "Partial IT Specialization": 1.5
    },
    "senior": {
        "Seniority": 3,
        "Max Programming Language": 8,
        "Max Tool/Framework": 15,
        "Max Certification": 4,
        "Max Programming Concept": 15,
        "Max IT Specialization": 4,
        "Full Programming Language": 5,
        "Partial Programming Language": 2,
        "Full Tool/Framework": 7,
        "Partial Tool/Framework": 3,
        "Full Certification": 4,
        "Partial Certification": 2,
        "Full Programming Concept": 2,
        "Partial Programming Concept": 1,
        "Full IT Specialization": 3,
        "Partial IT Specialization": 1.5
    }
}

VALIDATE_TEXT = """Wanted: Java Engineer with experience in building high-performing, scalable, enterprise-grade applications.
You need to have proven knowledge in Web applications with JEE/Spring, DevOps experience with high focus on cloud-based operating systems (particularly AWS), Jenkins, Docker and Kubernetes are a plus.
Looking for people with experience in Kafka, Big-Data and Python.
Must have experience with build tools (Maven, Gradle) and a Object-Oriented Analysis and design using common design patterns.
Hiring people with good knowledge of Relational Databases, PostgreSQL and ORM technologies (JPA, Hibernate).
Orientation towards test-driven development and clean code is a plus
Requirements: experience with version control systems (Git) and a Bachelor/Master degree in Computer Science, Engineering, or a related subject.
You need to have development experience in Java and Java frameworks and SQL/Relational Databases skills.
One requirement is having practical skills in CI/CD - some of Git, Maven, Gradle, Docker, Jenkins, Jira.
Skills description: 4+ years’ experience with Java (developing backend/web applications, Java 8+), 3+ years’ experience with Spring Boot (Spring Data, Spring Cloud), good unit/integration testing experience.
Nice-to-Have Skills: experience with software provisioning/configuration (e.g. Puppet, Ansible), with Oracle  and Angular 2+.
We are looking for: experience in Apache Camel, experience with MSSQL, PostgreSQL, experience with Unit and integration testing with JUnit and Mockito, CI/CD tools: Git, Jenkins, Maven, SonarQube, Artifactory and Microservices, Dockers, and Kubernetes.
Nice to have: exposure to NoSQL databases (MongoDBB), exposure to Python, Jupyter Hub.
Requirements: strong knowledge of Java Fundamentals and OOP principles and good understanding of design patterns.
At the moment we're using a mix of Python and Javascript.
We know you want to know so here is the stack: Python, Django, React, Redux, Express.
Other buzzwords: Universal Web Apps, Machine Learning, Heroku, AWS, Algolia.
Have already used at least one of these technologies amongst JavaScript, TypeScript, React, Vue.js, Kafka, ElasticSearch, MongoDB, and Python.
The general tech stack of the project is: iOS (Swift), Android (Kotlin), Modern Web Apps (Angular, React), Microservice architecture with OpenAPI contracts.
Basic qualifications: experience with web application development (.NET/JavaScript or equivalent).
Open to work with other programming languages (Python, Scala).
Qualifications and Experience: Knowledge of Spring (Boot, Data, Security).
University degree in a technical subject (Computer Science, Mathematics, or similar) or equivalent experience in the industry.
Qualifications: FPGA Digital Design experience, C++, Qt framework experience
The requirements are the following: knowledge of .Net, .Net Core, WebAPI, ASP.Net MVC, Razor Views or equivalent single page application framework, C#, JavaScript, CSS, HTML5 & Azure Cloud services or AWS, Active Directory.
You need to have experience with the ASP.NET framework and ideally SQL Server.
Capability to design complex SQL queries.
You know the ins and outs of several cloud providers like AWS, Azure, Heroku and profound experience in Terraform, Google Cloud.
Here are the technologies you must have experience with: Django, Node.js, Nginx, React, React Native, Redis, RabbitMQ.
The following are a must: Selenium, Grafana."""

TEST_TEXT = """Nice to have: Cloud certifications(Azure or AWS or GCP).
Experience with Jenkins pipelines and groovy scripting.
 We’re using Google Cloud SQL, Google Firestore, and other cloud services offered by Google Cloud.
Nice to have experience with SQL Server, REST API, Solid Principles, Microservices, Docker, TDD.
Hands-on coding expertise in object-oriented languages such as PHP.
Familiarity with Python and some of the following libraries: PyTorch, Tensorflow or Fast.ai, NumPy, OpenCV, scikit-learn.
Knowledge of Natural Language Generation or Natural Language Processing or Knowledge graph.
Practical knowledge of Data Mining, Machine Learning and Artificial Intelligence.
Understanding of SQL/NoSql database design and usage and experience with Vue or NodeJs.
Three or more years experience with HTML, CSS, and/or CSS Preprocessors
6 + months demonstrated experience in writing clean, high-quality HTML5, CSS3 and JavaScript cod
It is nice to have experience in a remote SCRUM team involving daily meetings, grooming, planning.
Experience with Git or similar version control."""

LABELS_LIST = {"Programming Language", "Certification", "Seniority", "Tool/Framework", "IT Specialization",
               "Programming Concept"}

TXT_FILES_DIRECTORY = "./utils/txt-amr-files"

TTL_FILES_DIRECTORY = "./utils/ttl-rdf-files"
