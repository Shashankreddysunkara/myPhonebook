    def customImage = ""
  node("linux") {

    stage("source") {
    git 'https://github.com/daximillian/myphonebook'
    }
    stage("build docker") {
    customImage = docker.build("daximillian/myphonebook")
    }
    stage("push to DockerHub") {
        echo "Push to Dockerhub"
    withDockerRegistry(credentialsId: 'dockerhub.daximillian') {
    customImage.push("${env.BUILD_NUMBER}")
    customImage.push("latest")
    }
    }
    stage("deploy to EKS") {
    sh '''
        export KUBECONFIG=/home/ubuntu/kubeconfig_opsSchool-eks
        kubectl apply -f deployment.yml
        kubectl set image deployment/phonebook phonebook=daximillian/myphonebook:"${BUILD_NUMBER}" --record
        kubectl apply -f service.yml
        kubectl apply -f loadbalancer.yml
        kubectl get svc phonebook-lb -o jsonpath="{.status.loadBalancer.ingress[*]['ip', 'hostname']}" > appUrl.txt
    '''
    }
    stage("slack message"){
        APP_URL = readFile('appUrl.txt').trim()
        slackSend color: "good", message: "Build  #${env.BUILD_NUMBER} Finished Successfully. App URL: ${APP_URL}"
    }
}
