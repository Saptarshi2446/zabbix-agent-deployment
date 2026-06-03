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

            script {

                sshagent(credentials: ['ansible-ssh-key']) {

                    def ansibleOutput = sh(
                        script: '''
                        ansible-playbook \
                          -i ansible/inventory.ini \
                          ansible/deploy_zabbix_agent.yml
                        ''',
                        returnStdout: true
                    ).trim()

                    echo ansibleOutput

                    def installedRunning = []
                    def serviceStarted = []
                    def newInstall = []

                    for (String line : ansibleOutput.split('\n')) {

                        if (line.contains("HOST_STATUS=")) {

                            def statusText = line.substring(
                                line.indexOf("HOST_STATUS=") + 12
                            )

                            def parts = statusText.split("\\|")

                            if (parts.length == 2) {

                                def host = parts[0].trim()
                                def status = parts[1].trim()

                                switch(status) {

                                    case "INSTALLED_AND_RUNNING":
                                        installedRunning.add(host)
                                        break

                                    case "SERVICE_STARTED":
                                        serviceStarted.add(host)
                                        break

                                    case "NEW_INSTALL":
                                        newInstall.add(host)
                                        break
                                }
                            }
                        }
                    }

                    echo "================================="
                    echo "DEPLOYMENT SUMMARY"
                    echo "================================="

                    if (!installedRunning.isEmpty()) {

                        echo "Installed and Running:"
                        echo installedRunning.join(', ')
                    }

                    if (!serviceStarted.isEmpty()) {

                        echo "Service Started:"
                        echo serviceStarted.join(', ')
                    }

                    if (!newInstall.isEmpty()) {

                        echo "New Installation:"
                        echo newInstall.join(', ')
                    }

                    echo "================================="
                }
            }
        }
    }
}

post {

    always {

        sh '''
        echo "Current known_hosts entries:"
        wc -l ~/.ssh/known_hosts || true
        '''
    }
}

}
