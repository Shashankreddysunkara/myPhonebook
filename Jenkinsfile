    def customImage = ""
  node("linux") {

    stage("source") {
    git 'https://github.com/daximillian/myPhonebook'
    }
    stage("build docker") {
    customImage = docker.build("daximillian/myPhonebook")
    }
    stage("verify image") {
        try {
    sh '''
        docker run --rm -d -p 8000:8080/tcp --name phonebook daximillian/myPhonebook
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
}