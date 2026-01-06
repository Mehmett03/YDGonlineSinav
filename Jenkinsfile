pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.11'
        TEST_BASE_URL = 'http://localhost:8000'
        SELENIUM_URL = 'http://localhost:4444/wd/hub'
    }

    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        // ===========================================
        // STAGE 1: Checkout
        // ===========================================
        stage('Checkout') {
            steps {
                echo '📥 Kaynak kodu çekiliyor...'
                checkout scm
            }
        }

        // ===========================================
        // STAGE 2: Setup Environment
        // ===========================================
        stage('Setup') {
            steps {
                echo '🔧 Python ortamı hazırlanıyor...'
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -r requirements-test.txt
                '''
            }
        }

        // ===========================================
        // STAGE 3: Unit Tests
        // ===========================================
        stage('Unit Tests') {
            steps {
                echo '🧪 Unit testler çalıştırılıyor...'
                sh '''
                    . venv/bin/activate
                    pytest tests/unit/ -v --junitxml=reports/unit-tests.xml --cov=app --cov-report=xml:reports/coverage.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/unit-tests.xml'
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        // ===========================================
        // STAGE 4: Integration Tests
        // ===========================================
        stage('Integration Tests') {
            steps {
                echo '🔗 Integration testler çalıştırılıyor...'
                sh '''
                    . venv/bin/activate
                    pytest tests/integration/ -v --junitxml=reports/integration-tests.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/integration-tests.xml'
                }
            }
        }

        // ===========================================
        // STAGE 5: Docker Build
        // ===========================================
        stage('Docker Build') {
            steps {
                echo '🐳 Docker imajları oluşturuluyor...'
                sh 'docker-compose build --no-cache'
            }
        }

        // ===========================================
        // STAGE 6: Start Services
        // ===========================================
        stage('Start Services') {
            steps {
                echo '🚀 Servisler başlatılıyor...'
                sh '''
                    docker-compose up -d
                    echo "Servislerin hazır olması bekleniyor..."
                    sleep 30
                    
                    # Health check
                    curl -f http://localhost:8000/health || exit 1
                    echo "✅ Servisler hazır!"
                '''
            }
        }

        // ===========================================
        // E2E TESTS (10 Ayrı Stage)
        // ===========================================
        
        stage('E2E: 01 - Login Success') {
            steps {
                echo '🔐 Senaryo 01: Başarılı Giriş testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_01_login_success.py -v --junitxml=reports/e2e-01.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-01.xml'
                }
            }
        }

        stage('E2E: 02 - Login Failure') {
            steps {
                echo '❌ Senaryo 02: Başarısız Giriş testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_02_login_failure.py -v --junitxml=reports/e2e-02.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-02.xml'
                }
            }
        }

        stage('E2E: 03 - Admin Create Exam') {
            steps {
                echo '📝 Senaryo 03: Admin Sınav Oluşturma testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_03_admin_create_exam.py -v --junitxml=reports/e2e-03.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-03.xml'
                }
            }
        }

        stage('E2E: 04 - Admin Add Questions') {
            steps {
                echo '❓ Senaryo 04: Admin Soru Ekleme testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_04_admin_add_questions.py -v --junitxml=reports/e2e-04.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-04.xml'
                }
            }
        }

        stage('E2E: 05 - Student View Exams') {
            steps {
                echo '👁️ Senaryo 05: Öğrenci Sınav Görüntüleme testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_05_student_view_exams.py -v --junitxml=reports/e2e-05.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-05.xml'
                }
            }
        }

        stage('E2E: 06 - Exam Completion') {
            steps {
                echo '✅ Senaryo 06: Sınav Tamamlama testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_06_exam_completion.py -v --junitxml=reports/e2e-06.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-06.xml'
                }
            }
        }

        stage('E2E: 07 - Timer Expiry') {
            steps {
                echo '⏱️ Senaryo 07: Süre Dolumu testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_07_timer_expiry.py -v --junitxml=reports/e2e-07.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-07.xml'
                }
            }
        }

        stage('E2E: 08 - Duplicate Prevention') {
            steps {
                echo '🚫 Senaryo 08: Tekrar Girme Engeli testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_08_duplicate_prevention.py -v --junitxml=reports/e2e-08.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-08.xml'
                }
            }
        }

        stage('E2E: 09 - Result Verification') {
            steps {
                echo '📊 Senaryo 09: Sonuç Doğrulama testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_09_result_verification.py -v --junitxml=reports/e2e-09.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-09.xml'
                }
            }
        }

        stage('E2E: 10 - Logout') {
            steps {
                echo '🚪 Senaryo 10: Çıkış testi...'
                sh '''
                    . venv/bin/activate
                    pytest tests/e2e/test_10_logout.py -v --junitxml=reports/e2e-10.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/e2e-10.xml'
                }
            }
        }
    }

    // ===========================================
    // POST ACTIONS
    // ===========================================
    post {
        always {
            echo '🧹 Temizlik yapılıyor...'
            sh 'docker-compose down -v || true'
            
            // Tüm test sonuçlarını topla
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
            
            // Test sonuç özeti
            echo '''
            ╔═══════════════════════════════════════╗
            ║     YDG ONLINE SINAV SİSTEMİ          ║
            ║     Test Sonuçları                    ║
            ╚═══════════════════════════════════════╝
            '''
        }
        success {
            echo '''
            ✅ ════════════════════════════════════════
               TÜM TESTLER BAŞARIYLA TAMAMLANDI!
            ════════════════════════════════════════ ✅
            '''
        }
        failure {
            echo '''
            ❌ ════════════════════════════════════════
               BAZI TESTLER BAŞARISIZ OLDU!
               Lütfen test raporlarını inceleyin.
            ════════════════════════════════════════ ❌
            '''
        }
        cleanup {
            cleanWs()
        }
    }
}
