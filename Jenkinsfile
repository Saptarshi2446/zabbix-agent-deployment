pipeline {

    agent any

    environment {

        INVENTORY_FILE = "ansible/inventory.ini"
        CSV_FILE = "ansible/inventory/hosts.csv"
    }

    stages {

        stage('Validate CSV') {

            steps {

                script {

                    if (!fileExists(env.CSV_FILE)) {

                        error("hosts.csv file not found")
                    }

                    def csvContent = readFile(env.CSV_FILE)

                    if (!csvContent.contains("hostname,ip,os,username")) {

                        error("CSV headers are invalid")
                    }

                    echo "CSV validation successful"
                }
            }
        }

        stage('Generate Inventory') {

            steps {

                sh '''
                python3 scripts/generate_inventory.py
                '''

                sh '''
                cat ansible/inventory.ini
                '''
            }
        }

        stage('Validate Connectivity') {

            steps {

                sshagent(credentials: ['ansible-ssh-key']) {

                    sh '''
                    ansible all \
                      -i ansible/inventory.ini \
                      -m ping
                    '''
                }
            }
        }

        stage('Deploy Zabbix Agent') {

            steps {

                sshagent(credentials: ['ansible-ssh-key']) {

                    sh '''
                    ansible-playbook \
                      -i ansible/inventory.ini \
                      ansible/deploy_zabbix_agent.yml
                    '''
                }
            }
        }
    }

    post {

        success {

            echo 'Zabbix Agent deployment completed successfully'
        }

        failure {

            echo 'Deployment failed'
        }
    }
}
