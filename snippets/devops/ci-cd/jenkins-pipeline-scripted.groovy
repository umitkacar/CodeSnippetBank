node {
    def app
    def registry = 'registry.example.com'
    def imageName = 'myapp'

    try {
        stage('Checkout') {
            checkout scm
            env.GIT_COMMIT_SHORT = sh(
                script: "git rev-parse --short HEAD",
                returnStdout: true
            ).trim()
        }

        stage('Build') {
            sh 'npm ci'
            sh 'npm run build'
        }

        stage('Test') {
            parallel(
                'Unit Tests': {
                    sh 'npm run test:unit'
                },
                'Integration Tests': {
                    sh 'npm run test:integration'
                }
            )
        }

        stage('Docker Build') {
            app = docker.build("${registry}/${imageName}:${env.GIT_COMMIT_SHORT}")
        }

        stage('Push Image') {
            docker.withRegistry("https://${registry}", 'docker-credentials') {
                app.push("${env.GIT_COMMIT_SHORT}")
                app.push('latest')
            }
        }

        stage('Deploy') {
            input message: 'Deploy to production?', ok: 'Deploy'
            sh """
                kubectl set image deployment/myapp \
                myapp=${registry}/${imageName}:${env.GIT_COMMIT_SHORT} \
                -n production
            """
        }

        currentBuild.result = 'SUCCESS'
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        stage('Cleanup') {
            cleanWs()
        }

        // Send notifications
        def color = currentBuild.result == 'SUCCESS' ? 'good' : 'danger'
        slackSend(
            color: color,
            message: "Build ${env.BUILD_NUMBER}: ${currentBuild.result}"
        )
    }
}
