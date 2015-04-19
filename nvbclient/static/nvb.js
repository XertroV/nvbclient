(function(){
    COIN = Math.pow(10, 8); // 100,000,000

    createVote = function(type, params){
        return {type: type, params: params}
    };

    setupVoteHoster = function($http, $scope, $log, host, type){
        host.msg = ''
        host.showMsg = false;
        host.loading = false;

        host.make = function(){
            host.loading = true;
            host.showMsg = false;
            $http.post('/sign_vote.json', {password: $scope.login.password, vote: createVote(type, host.makeParams())})
                .success(function(data){
                    host.showMsg = true;
                    host.msg = data.msg;
                    host.loading = false;
                })
                .error(function(error,and,other,things){
                    $log.log(error);
                    host.loading = false;
                });
        }
    };

    app = angular.module("nvbApp", [])

    app.controller("LoginController", ['$http', '$log', function($http, $log){
        var login = this;

        login.reset = function(){
            login.authenticated = false;
            login.password = '';
            login.address = '';
            login.testnetAddress = '';
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
                        login.testnetAddress = data.testnet_address
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

    app.controller('VoteController', ['$http', '$scope', '$log', function($http, $scope, $log){
        var voteCtrl = this;
        voteCtrl.voteNumber = 0;
        voteCtrl.min = 0;
        voteCtrl.max = 255;
        voteCtrl.resolution = 'RES-ID';

        voteCtrl.asPercentage = function(){return voteCtrl.voteNumber / voteCtrl.max * 100;};

        voteCtrl.makeParams = function(){return { vote_number: voteCtrl.voteNumber, resolution: voteCtrl.resolution};};

        setupVoteHoster($http, $scope, $log, voteCtrl, 'cast');
    }]);

    app.controller('DelegateController', ['$http', '$scope', '$log', function($http, $scope, $log){
        var dlgCtrl = this;
        dlgCtrl.address = '';
        dlgCtrl.categories = 255;  // currently unused but could provide some ways to mix and match delegation

        dlgCtrl.makeParams = function(){
            return {address: dlgCtrl.address, categories: dlgCtrl.categories};
        }

        setupVoteHoster($http, $scope, $log, dlgCtrl, 'delegate');
    }]);

    app.controller('CommentController', ['$http', '$scope', '$log', function($http, $scope, $log){
        var comment = this;
        comment.text = '';

        comment.makeParams = function(){
            return {comment: comment.text};
        }

        setupVoteHoster($http, $scope, $log, comment, 'comment');
    }]);

    app.controller('ResolutionController', ['$http', '$scope', '$log', function($http, $scope, $log){
        var resCtrl = this;
        resCtrl.endTimestamp = 0;
        resCtrl.name = '';
        resCtrl.url = '';
        resCtrl.categories = 255;

        resCtrl.makeParams = function(){
            return {end_timestamp: resCtrl.endTimestamp, resolution: resCtrl.name, url: resCtrl.url, categories: resCtrl.categories};
        }

        setupVoteHoster($http, $scope, $log, resCtrl, 'mod_res');
    }]);

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
            if($scope.login.authenticated){f();}
            else{setTimeout(function(){starter(f)}, 500);}
        }

        jobs.jobs.forEach(function(job){
            starter(job.start);
        });
    }]);

    app.controller('NewNetworkController', ['$http', '$scope', '$log', function($http, $scope, $log){
        var newCtrl = this;

        newCtrl.name = '';

        newCtrl.makeParams = function(){return {name: newCtrl.name};};

        setupVoteHoster($http, $scope, $log, newCtrl, 'create');
    }]);

    app.controller('EmpowerController', ['$http', '$scope', '$log', function($http, $scope, $log){
        var empCtrl = this;
        empCtrl.votes = 0;
        empCtrl.address = '';

        empCtrl.makeParams = function(){return {votes: empCtrl.votes, address: empCtrl.address};};

        setupVoteHoster($http, $scope, $log, empCtrl, 'empower');
    }]);

    app.controller('InfoController', ['$http','$log', function($http, $log){
        var info = this;
        info.rate = 1;

        info.setRate = function(r){
            info.rate = r / COIN;
        }
        info.setRate(300);

        $http.get('https://bitpay.com/api/rates').
            success(function(data){
                data.forEach(function(d){
                    if(d.code == "AUD"){ info.setRate(d.rate); }
                })
            }).error(function(error,and,other,things){
                $log.log(error);
        });
    }]);
})();