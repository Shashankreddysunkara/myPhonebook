    def customImage = ""
  node("linux") {
    stage("source") {
    git 'https://github.com/Shashankreddysunkara/myPhonebook.git'
    }
    stage("build docker") {
    customImage = docker.build("dock101/myphonebook")
    }
    stage("verify image") {
        try {
            sh '''
                export PB_HOST=$(dig +short mysql.service.consul)      
                export PB_USER=phoneapp
                export PB_PASS=123456
                export PB_DB=phonebook
                export PB_PORT=3306
                export PB_LOG=info
                docker run -d -p 8000:8000/tcp -e PB_HOST -e PB_USER \
                -e PB_PASS -e PB_DB -e PB_PORT -e PB_LOG --name phonebook dock101/myphonebook
                sleep 20s
                curl_response=$(curl -s -o /dev/null -w "%{http_code}" 'http://localhost:8000')
                if [ $curl_response -eq 200 ]
                then
                    exit 0
                else
                    exit 1
                fi
            '''  
        }   
        catch (Exception e) {
            sh '''
                docker stop phonebook
                #docker rm phonebook -f
            '''
        }  
    }
    // stage("cleanup image") {
    // sh '''
    //     docker stop phonebook
    // '''
    // }
    stage("push to DockerHub") {
        echo "Push to Dockerhub"
    withDockerRegistry(credentialsId: 'dockerhub.creds') {
    customImage.push("${env.BUILD_NUMBER}")
    customImage.push("latest")
    }
    }
    stage("set up secrets") {
        try {
    sh '''
        export KUBECONFIG=/home/ubuntu/kubeconfig_ops-eks
        kubectl create -f boring-data.yml
    '''
    } catch (Exception e) {
    sh '''
        export KUBECONFIG=/home/ubuntu/kubeconfig_ops-eks
        kubectl delete -f boring-data.yml
        kubectl create -f boring-data.yml
    '''
        }     
    }
    stage("deploy to EKS") {
    sh '''
        export KUBECONFIG=/home/ubuntu/kubeconfig_ops-eks
        MYSQL_IP=$(dig +short mysql.service.consul)
        kubectl apply -f deployment.yml
        kubectl set env deployment/phonebook PB_HOST=$MYSQL_IP
        kubectl set image deployment/phonebook phonebook=dock101/myphonebook:"${BUILD_NUMBER}" --record
        kubectl apply -f service.yml
        kubectl apply -f loadbalancer.yml
        sleep 20s
        kubectl get svc phonebook-lb -o jsonpath="{.status.loadBalancer.ingress[*]['ip', 'hostname']}" > appUrl.txt
    '''
    }
    stage("apply HPA") {
        try {
    sh '''
        export KUBECONFIG=/home/ubuntu/kubeconfig_ops-eks
        kubectl autoscale deployment phonebook --cpu-percent=70 --min=1 --max=4
    '''
     } catch (Exception e) {
    sh '''
        export KUBECONFIG=/home/ubuntu/kubeconfig_ops-eks
        kubectl delete hpa phonebook
        kubectl autoscale deployment phonebook --cpu-percent=70 --min=1 --max=4
    '''
        }
    }
    // stage("performance test") {
    // sh '''
    //     export KUBECONFIG=/home/ubuntu/kubeconfig_ops-eks
    //     APP_URL=$(kubectl get svc phonebook-lb -o jsonpath="{.status.loadBalancer.ingress[*]['ip', 'hostname']}")
    //     sed 's/@SERVER@/'$APP_URL'/g' load-test.jmx > load-test-act.jmx
    //     jmeter -n -t load-test-act.jmx -l /home/ubuntu/load-test-"${BUILD_NUMBER}".jtl 
    // '''
    //}
    stage("slack message"){
        APP_URL = readFile('appUrl.txt').trim()
        slackSend color: "good", message: "Build  #${env.BUILD_NUMBER} Finished Successfully. App URL: ${APP_URL}"
    }
}
