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
                echo "Generated Inventory:"
                cat ansible/inventory.ini
                '''
            }
        }

        stage('Update Known Hosts') {

            steps {

                sh '''
                mkdir -p ~/.ssh
                touch ~/.ssh/known_hosts

                for ip in $(grep ansible_host ansible/inventory.ini | awk -F'ansible_host=' '{print $2}' | awk '{print $1}')
                do
                    echo "Processing $ip"

                    ssh-keyscan -H $ip >> ~/.ssh/known_hosts 2>/dev/null || true
                done

                chmod 700 ~/.ssh
                chmod 644 ~/.ssh/known_hosts
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

        always {

            sh '''
            echo "Current known_hosts entries:"
            wc -l ~/.ssh/known_hosts || true
            '''
        }
    }
}
