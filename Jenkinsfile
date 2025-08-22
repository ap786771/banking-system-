pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "banking_system"
        DOCKER_TAG = "latest"
        SONARQUBE_SERVER = "SonarQube" // Jenkins SonarQube server name
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/yourusername/banking-system.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_SERVER}") {
                    sh "sonar-scanner \
                        -Dsonar.projectKey=BankingSystem \
                        -Dsonar.sources=app \
                        -Dsonar.tests=tests \
                        -Dsonar.python.version=3.10 \
                        -Dsonar.host.url=${env.SONAR_HOST_URL} \
                        -Dsonar.login=${env.SONAR_AUTH_TOKEN}"
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh "pytest tests/ --junitxml=results.xml"
            }
            post {
                always {
                    junit 'results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $DOCKER_IMAGE:$DOCKER_TAG ."
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh """
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                        docker tag $DOCKER_IMAGE:$DOCKER_TAG $DOCKER_USERNAME/$DOCKER_IMAGE:$DOCKER_TAG
                        docker push $DOCKER_USERNAME/$DOCKER_IMAGE:$DOCKER_TAG
                    """
                }
            }
        }

        stage('Deploy Docker Container') {
            steps {
                sh """
                    docker stop banking_system || true
                    docker rm banking_system || true
                    docker run -d -p 5000:5000 --name banking_system $DOCKER_IMAGE:$DOCKER_TAG
                """
            }
        }
    }

    post {
        always {
            echo "Pipeline finished"
        }
    }
}
