(function(){
    app = angular.module("nvbApp", [])

    app.controller("LoginController", ['$http', '$log', function($http, $log){
        var login = this;

        login.reset = function(){
            login.authenticated = false;
            login.password = '';
            login.address = '';
            login.n_utxos = 0;
            login.balance = 0;
        };
        login.reset();

        login.tryPassword = function(password){
            password = password || '';
            $http.post('/check_password.json', {password:password}).
                success(function(data){
                    if (data.result == true){
                        login.authenticated = true;
                        login.address = data.address;
                        login.n_utxos = data.n_utxos;
                        login.balance = data.balance;
                    } else {
                        login.reset();
                    }
                }).
                error(function(data, status, headers, config){
                    $log.log(data);
                    login.reset();
                });
        };

        login.changePassword = function(oldpw, newpw1, newpw2){
            if(oldpw != login.password) return false;
            if(newpw1 != newpw2) return false;
            $http.post('/change_password.json', {password: newpw1}).
                success(function(data){

                });
        }

        login.tryPassword();
    }]);

    app.controller('TabController', ['$log', function($log){
        var tab = this;
        tab.tabsLeft = ['info', 'vote', 'admin'];
        tab.tabsRight = ['settings', 'about'];

        tab.set = function(t){
            tab.current = t;
            $log.log('Setting tab to: ' + t);
        }
        tab.set('info');

        tab.is = function(t){
            return (t == tab.current);
        }
    }]);

    app.controller('ChangePasswordController', ['$http', '$scope', function($http, $scope){
        var cpwCtrl = this;
        cpwCtrl.error = {status: false, message: ''};
        cpwCtrl.success = {status: false, message: ''};
        cpwCtrl.oldPassword = '';
        cpwCtrl.newPassword = '';
        cpwCtrl.newPasswordConf = '';

        cpwCtrl.changePassword = function(){
            cpwCtrl.success.status = false;
            cpwCtrl.error.status = false;
            if (cpwCtrl.oldPassword != $scope.login.password){
                cpwCtrl.error.status = true;
                cpwCtrl.error.message = 'Old Password Incorrect.';
                return false;
            } else if (cpwCtrl.newPassword != cpwCtrl.newPasswordConf) {
                cpwCtrl.error.status = true;
                cpwCtrl.error.message = 'New Passwords Do Not Match.'
                return false;
            } else {
                $http.post('/change_password.json', {password: cpwCtrl.oldPassword, new_password: cpwCtrl.newPassword}).
                    success(function(data){
                        if (data.result = true){
                            cpwCtrl.success.status = true;
                            cpwCtrl.success.message = data.message;
                            $scope.login.password = cpwCtrl.newPassword;
                        } else {
                            cpwCtrl.error.status = true;
                            cpwCtrl.error.message = data.message;
                        }
                    }).error();
                cpwCtrl.error.status = false;
                return true;
            }
        }
    }]);

    app.controller('VoteController', function(){
        var voteCtrl = this;
        voteCtrl.voteNumber = 0;
        voteCtrl.min = 0;
        voteCtrl.max = 255;

        voteCtrl.asPercentage = function(){return voteCtrl.voteNumber / voteCtrl.max * 100};
    })

    app.controller('DelegateController', function(){
        var dlgCtrl = this;
        dlgCtrl.delegateAddress = '';
        dlgCtrl.delegateClass = 0;
    });

    app.controller('ResolutionController', function(){
        var resCtrl = this;
        resCtrl.close = 0;
        resCtrl.name = '';
        resCtrl.url = '';
    });

    app.controller('BatchJobController', ['$http', '$scope', '$log', function($http, $scope, $log){
        var jobs = this;

        jobs.jobs = [
            {
                name: "update_utxos",
                start: function () {
                    jobs.jobs[0].prettyDone = 'running';
                    $http.post('/update_utxos.json', {password: $scope.login.password}).
                        success(function(data){
                            if (data.updated){
                                jobs.jobs[0].prettyDone = 'done';
                                jobs.jobs[0].done = true;
                                $scope.login.n_utxos = data.n_utxos;
                                $scope.login.balance = data.balance;
                            } else {
                                jobs.jobs[0].prettyDone = 'error';
                                $log.log(data);
                            }
                        }).
                        error(function(error,some,other,stuff){
                            jobs.jobs[0].prettyDone = 'error';
                            $log.log(jobs.jobs[0].prettyDone);
                        });
                },
                done: false,
                prettyDone: 'waiting',
            }
        ];

        jobs.all = function(){return jobs.jobs;}

        var starter = function(f){
            $log.log('a');
            if($scope.login.authenticated){f();}
            else{setTimeout(function(){starter(f)}, 500);}
        }

        jobs.jobs.forEach(function(job){
            starter(job.start);
        });
    }]);

    app.controller('NewNetworkController', ['$http', '$scope', function($http, $scope){
        var newCtrl = this;

        newCtrl.name = '';
        newCtrl.status = false;
        newCtrl.message = '';

        newCtrl.make = function(){
            $http.post('/sign_vote.json', {password: $scope.login.password, vote: {type: 'new', params: {name: newCtrl.name}}}).
                success(function(data){
                    newCtrl.status = data.result;
                    newCtrl.message = data.tx;
                }).error(function(){
                    newCtrl.status = true;
                    newCtrl.message = 'error';
                });
        };
    }]);

    app.controller('EmpowerController', ['$http', function($http){
        var empCtrl = this;
        empCtrl.votes = 0;
        empCtrl.address = '';
    }]);
})();