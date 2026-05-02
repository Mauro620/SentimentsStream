pipelineJob('SentimentStream') {
    description('End-to-end Big Data sentiment pipeline — IUE Big Data 2026-1')

    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url('file:///var/jenkins_home/workspace/SentimentStream')
                    }
                    branch('*/main')
                }
            }
            scriptPath('infra/jenkins/Jenkinsfile')
        }
    }

    triggers {
        pollSCM('H/5 * * * *')
    }
}
