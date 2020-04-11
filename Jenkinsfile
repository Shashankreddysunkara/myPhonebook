    def customImage = ""
  node("linux") {

    stage("source") {
    git 'https://github.com/daximillian/myphonebook'
    }
    stage("build docker") {
    customImage = docker.build("daximillian/myphonebook")
    }
    stage("verify image") {
        try {
    sh '''
        PB_HOST=$(dig +short mysql.service.consul)
        PB_USER='phoneapp'
        PB_PASS='123456'
        PB_DB='phonebook'
        PB_PORT='3306'
        PB_LOG='info'
        docker run --rm -d -p 8000:8000/tcp --name phonebook daximillian/myphonebook -e PB_HOST -e PB_USER \
        -e PB_PASS -e PB_DB -e PB_PORT -e PB_LOG
        sleep 20s
        curl_response=$(curl -s -o /dev/null -w "%{http_code}" 'http://localhost:8000')
        if [ $curl_response -eq 200 ]
        then
            exit 0
        else
            exit 1
        fi
    ''' 
    } catch (Exception e) {
    sh '''
        docker stop phonebook
    '''
    }  
    }
    stage("cleanup image") {
    sh '''
        docker stop phonebook
    '''
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
        kubectl create -f boring-data.yml
        MYSQL_IP=$(dig +short mysql.service.consul)
        kubectl apply -f deployment.yml
        kubectl set env deployment/phonebook PB_HOST=$MYSQL_IP
        kubectl set image deployment/phonebook phonebook=daximillian/myphonebook:"${BUILD_NUMBER}" --record
        kubectl apply -f service.yml
        kubectl apply -f loadbalancer.yml
        sleep 20s
        kubectl get svc phonebook-lb -o jsonpath="{.status.loadBalancer.ingress[*]['ip', 'hostname']}" > appUrl.txt
    '''
    }
    stage("slack message"){
        APP_URL = readFile('appUrl.txt').trim()
        slackSend color: "good", message: "Build  #${env.BUILD_NUMBER} Finished Successfully. App URL: ${APP_URL}"
    }
}
