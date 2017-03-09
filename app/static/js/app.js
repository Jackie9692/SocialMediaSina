angular.module("app", ['chart.js', 'rzModule', 'ui.bootstrap', 'uiSwitch', 'ngAnimate', 'ngRoute', 'ngSanitize', 'vAccordion'])

.config(['$routeProvider', function($routeProvider) {
	for (menu of menuList) {
		let url = '/' + menu.url;
		
		if (menu.subMenuList.length > 0) {
			$routeProvider.when(url,{redirectTo: url +'/' + menu.subMenuList[0].url});
			for (subMenu of menu.subMenuList) {
				let subUrl = '/' + subMenu.url;
				$routeProvider.when(url + subUrl,{
					templateUrl: subUrl
				});
			}
		}
		else
			$routeProvider.when(url,{
				templateUrl: url
			});
	}

	for (url of otherUrl) {
		url = '/' + url;
		$routeProvider.when(url,{templateUrl: url});
	}
    $routeProvider.otherwise({redirectTo:'/home'});
}])

.run(function ($rootScope, $location, $route, AuthService) {
	$rootScope.$on('$routeChangeStart', function (event, next, current) {
		AuthService.getUserStatus().then(function(){
			if (next.loadedTemplateUrl !='/home' && !AuthService.isLoggedIn()){
				console.log('Require to be logged in to access this page')
				$location.path('/home');
				$route.reload();
			}
		});
	});
})

.factory('AuthService',	function($q, $timeout, $http) {
	// create user variable
	var user = false;

	// return available functions for use in controllers
	return ({
		isLoggedIn: isLoggedIn,
		login: login,
		logout: logout,
		getUserStatus: getUserStatus
	});

	function isLoggedIn() {
		if(user) {
			return true;
		}
		else {
			return false;
		}
	}

	function login(email, password) {
		// create a new instance of deferred
		var deferred = $q.defer();

		// send a post request to the server
		$http.post('/login', {email: email, password: password})
		// handle success
		.success(function (data, status) {
			if(status === 200 && data.result){
				user = true;
				deferred.resolve();
			}
			else {
				user = false;
				deferred.reject();
			}
		})
		// handle error
		.error(function (data) {
			user = false;
			deferred.reject();
		});

		// return promise object
		return deferred.promise;
	}

	function logout() {
		// create a new instance of deferred
		var deferred = $q.defer();

		// send a get request to the server
		$http.get('/logout')
		// handle success
		.success(function (data) {
			console.log('test')
			user = false;
			deferred.resolve();
		})
		// handle error
		.error(function (data) {
			user = false;
			deferred.reject();
		});

		// return promise object
		return deferred.promise;
	}

	function getUserStatus() {
		return $http.get('/status')
		// handle success
		.success(function (data) {
			if(data.status){
				user = true;
			}
			else {
				user = false;
			}
		})
			// handle error
		.error(function (data) {
			user = false;
		});
	}
})

.controller('LayoutCtrl', function ($scope, $location, $uibModal, AuthService) {
	$scope.menuList = menuList;
	$scope.location = {};
	$scope.title = function() {
		let res = ""
		for (menu of menuList) {
			if (menu.url == $scope.location.menu) {
				res = "<h1>" + menu.text;
				for (subMenu of menu.subMenuList) {
					if (subMenu.url == $scope.location.subMenu) {
						res += " <small>"+subMenu.text+"</small>";
						break;
					}
				}
				break;
			}
		}
		return res;
	}

	$scope.$on('$locationChangeSuccess', function(event) {
		[dump, menuUrl, subMenuUrl] = $location.path().split('/');
		$scope.accordion.collapseAll();
		$scope.accordion.expand(menuUrl);
		$scope.location.menu = menuUrl;
		$scope.location.subMenu = subMenuUrl;
	});

	$scope.logged_in = false;//here

	$scope.login = function() {
		var modalInstance = $uibModal.open({
			animation: true,
			templateUrl: 'login.html',
			controller: 'LoginCtrl',
			size: 'md',
			resolve: {
				login: function() {
					return function() {
						$scope.logged_in = true;
					}
				}
			}
		});
		$scope.logged_in = false;
	};
	$scope.logout = function() {
		$scope.logged_in = false;
		AuthService.logout()
	};
})

.controller('LoginCtrl', function ($scope, $uibModalInstance, AuthService, login) {
	$scope.login = function () {
		$scope.error = false;
		$scope.disabled = true;

		// call login from service
		AuthService.login($scope.loginForm.email, $scope.loginForm.password)
		// handle success
		.then(function () {
			if (AuthService.isLoggedIn) {
				login();
			}
			$scope.disabled = false;
			$scope.loginForm = {};
		})
		// handle error
		.catch(function () {
			$scope.error = true;
			$scope.errorMessage = "Invalid username and/or password";
			$scope.disabled = false;
			$scope.loginForm = {};
		});
		$uibModalInstance.close();
	};
});

var Menu = function (text, icon, url, hide) {
	this.text = text;
	this.icon = "glyphicon glyphicon-" + icon;
	this.url = url;
	this.hide = (hide != undefined)? hide : false;
	this.subMenuList = [];
};

//menuList
home = new Menu("Home", "home", "home");

statistics = new Menu("Statistics", "stats", "statistics");
time_statistics = new Menu("Time", "chevron-right", "time_statistics");
sentiment_statistics = new Menu("Sentiment", "chevron-right", "sentiment_statistics");
location_statistics = new Menu("Location", "chevron-right", "location_statistics");
keywords_statistics = new Menu("Keywords", "chevron-right", "keywords_statistics");
statistics.subMenuList = [time_statistics, sentiment_statistics, location_statistics, keywords_statistics];

data_analysis = new Menu("Data Analysis", "dashboard", "data_analysis");
status_analysis = new Menu("Status Analysis", "chevron-right", "status_analysis", true);
user_analysis = new Menu("User Analysis", "chevron-right", "user_analysis", true);
event_analysis = new Menu("Event Analysis", "chevron-right", "event_analysis", true);
data_analysis.subMenuList = [status_analysis, user_analysis, event_analysis];

search = new Menu("Search", "search", "search");
quick_search = new Menu("Quick Search", "chevron-right", "quick_search");
search_status = new Menu("Status & Comment", "chevron-right", "search_status");
search_user = new Menu("User", "chevron-right", "search_user");
search_event = new Menu("Event", "chevron-right", "search_event");
status_list_visualisation = new Menu("Status List Visualisation", "chevron-right", "status_list_visualisation", true);
user_list_visualisation = new Menu("User List Visualisation", "chevron-right", "user_list_visualisation", true);
event_list_visualisation = new Menu("Event List Visualisation", "chevron-right", "event_list_visualisation", true);
search.subMenuList = [quick_search, search_status, search_user, search_event, status_list_visualisation, user_list_visualisation, event_list_visualisation];

manage = new Menu("Manage", "option-vertical", "manage");
data_cleaning = new Menu("Data Cleaning", "chevron-right", "data_cleaning")
manage.subMenuList = [data_cleaning]
settings = new Menu("Settings", "cog", "settings");
help = new Menu("Help", "question-sign", "help");

var menuList = [
	home,
	statistics,
	data_analysis,
	search,
	manage,
	settings,
	help
];

var otherUrl = [
	"status_visualisation",
];