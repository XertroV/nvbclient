(function(){
    app = angular.module("nvbApp", [])

    app.controller("LoginController", ['$http', '$log', function($http, $log){
        var login = this;

        login.reset = function(){
            login.authenticated = false;
            login.password = '';
        };
        login.reset();

        login.tryPassword = function(password){
            password = password || '';
            $http.post('/check_password.json', {password:password}).
                success(function(data){
                    if (data.result == true){
                        login.authenticated = true;
                        login.address = data.address;
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

        cpwCtrl.changePassword = function(oldpw, oldpw_conf, newpw, newpw_conf){
            if (oldpw != oldpw_conf){
                cpwCtrl.error.status = true;
                cpwCtrl.error.message = 'Old Password Incorrect.'
                return false;
            } else if (newpw != newpw_conf) {
                cpwCtrl.error.status = true;
                cpwCtrl.error.message = 'New Passwords Do Not Match.'
                return false;
            } else {
                $http.post('/change_password.json', {old_password: oldpw, new_password: newpw}).
                    success(function(data){
                        if (data.result = true){
                            cpwCtrl.success.status = true;
                            cpwCtrl.success.message = data.message;
                            $scope.login.password = new_password;
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
})();