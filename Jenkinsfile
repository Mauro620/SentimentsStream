pipeline {
    agent any

    environment {
        GIT_SHA = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        COMPOSE  = 'docker compose -f infra/compose/docker-compose.yml --project-name sentimentstream'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    pip install --quiet ruff black --break-system-packages
                    python3 -m ruff check services/api/src services/spark-pipeline/src
                    python3 -m black --check services/api/src services/spark-pipeline/src
                '''
            }
        }

        stage('Unit Tests') {
            parallel {
                stage('API') {
                    steps {
                        sh '''
                            pip install --quiet -r services/api/requirements.txt --break-system-packages
                            cd services/api && python3 -m pytest tests/unit -v --tb=short
                        '''
                    }
                }
                stage('Spark Pipeline') {
                    steps {
                        sh '''
                            pip install --quiet -r services/spark-pipeline/requirements.txt --break-system-packages
                            cd services/spark-pipeline && python3 -m pytest tests/unit -v --tb=short
                        '''
                    }
                }
            }
        }

        stage('Build Images') {
            steps {
                sh "${COMPOSE} build --no-cache"
                sh "docker tag sentimentstream-api:latest sentimentstream-api:${GIT_SHA}"
            }
        }

        stage('Integration Tests') {
            steps {
                sh "${COMPOSE} up -d mongo"
                sh 'sleep 15'
                sh '''
                    pip install --quiet pytest --break-system-packages
                    cd services/api && python3 -m pytest tests/integration -v --tb=short
                '''
            }
            post {
                always {
                    sh "${COMPOSE} down || true"
                }
            }
        }

        stage('Deploy') {
            steps {
                sh "${COMPOSE} up -d --build"
                sh 'sleep 20'
            }
        }

        stage('Smoke') {
            steps {
                sh 'bash scripts/run_e2e_smoke.sh'
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed. Check logs above."
        }
        success {
            echo "Pipeline passed. SHA: ${GIT_SHA}"
        }
    }
}