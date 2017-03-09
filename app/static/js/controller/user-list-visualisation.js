angular.module("app").controller("UserListVisualisationCtrl", function ($scope, $controller, userListVisualisationService, userService) {
	$controller('ListVisualisationCtrl', {$scope: $scope, listVisualisationService: userListVisualisationService});

	$scope.state = userListVisualisationService;

	$scope.visualize = function(user) {
		userService.load(user);
	};
})

.service('userListVisualisationService', function($http) {
	var page = 1;
	var orderBy = "date";
	var reverse = false;

	var userList = [];
	var trueTotalItems = 0;
	var totalItems = 0;

	var loading = true;

	var params = undefined;

	return {
		page: page,
		orderBy: orderBy,
		reverse: reverse,
		userList: userList,
		trueTotalItems: trueTotalItems,
		totalItems: totalItems,
		loading: loading,

		setParams: function(state) {
			params = state;
		},
		search: function() {
			if (params != undefined) {
				scope = this

				this.loading = true;

				params.request = "userList";
				params.page =  this.page - 1;
				params.orderBy = this.orderBy;
				params.reverse = this.reverse;

				console.log("Sending search request to sever");
				$http({
					url: "search_request", 
					method: "GET",
					params: params
				}).then(function(response) {
					console.log("Receiving answer")
					scope.userList = response.data.hits;
					scope.trueTotalItems = response.data.total;
					scope.totalItems = response.data.total< 10000? response.data.total : 10000;
					scope.loading = false;
				});
				return true;
			}
			return false;
		},
	};
});