pipeline {
    agent any

    // Build options (some of these can no longer be set through the Jenkins UI because Build Environment tab is gone)
    options {
        ansiColor('xterm')
    }

    // Assign env variables for all stages. Can call functions defined outside pipeline{}
    environment {

    }

    stages {
        stage('Install-Required-Libs') {
            steps {
                sh 'virtualenv env'
                sh 'env/bin/pip3 install .'
                sh 'env/bin/pip3 install --no-cache-dir -r requirements.txt'
            }
        }
        stage('Analysis') {
            parallel {
                stage('Lint') {
                    steps {
                        title 'Lint'
                        sh 'env/bin/pylint --output-format=parseable --reports=y pylint_exit_options.py || env/bin/pylint-exit-options --exit-report=F,E,W,R,C,U $?'
                    }
                }
            }
        }
    }
}

def updateIniValue(String path, String section, String key, String value) {
    // Don't put comments after brackets on section titles, it will break regex.
    def startBounds = "/^\\[$section\\]\$/"
    def search = "/^$key = .*/"
    def replace = "$key = $value"
    myBash "sed -i '$startBounds,/^\\[/ s$search" + "$replace/' $path"
}

def title(String name) {
    echo "\033[36m \n[ $name ] \033[0m \n"
    env.LAST_STAGE_NAME = name
}

def info(String text) {
    echo "\033[33m[Info]    \033[0m $text"
}

def error(String text) {
    echo "\033[31m[Error]   \033[0m $text"
}

def success(String text) {
    echo "\033[32m[Success] \033[0m $text"
}
