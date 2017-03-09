angular.module("app").controller("UserAnalysisCtrl", function ($scope, userService, statusListVisualisationService) {
	$scope.state = userService;

	$scope.search = function () {
		statusListVisualisationService.setParams({
			"user_id": $scope.state.user.user_id
		});
	};
})

.service('userService', function($http) {
	var user = undefined;
	/*user = {
		name: '名字',
		screen_name: '名字',
		gender: 'male',
		description: "Description goes here",
		profile_url: "url.com",
		url: "url.com",
		location: "上海",
		lang: "zh",
		followers_count: 3842,
		created_at: "2015-05-24T15:45:03",
		friends_count: 59,
		category: "Common",
		score: 50,
	}*/

	var load = function(user) {
		if (user.screen_name == undefined)
			user.screen_name = user.name;
		if (user.gender == undefined)
			user.gender = "N/A";
		if (user.location == undefined)
			user.location = "N/A";
		if (user.statuses_count == undefined)
			user.statuses_count = "N/A";
		if (user.lang == undefined)
			user.lang = "N/A";
		if (user.followers_count == undefined)
			user.followers_count = "N/A";
		if (user.friends_count == undefined)
			user.friends_count = "N/A";
		if (user.verified_reason == undefined)
			user.verified_reason = "N/A";
		if (user.category == undefined)
			user.category = "Normal";
		if (user.score == undefined)
			user.score = 50;

		this.user = user;
	};

	return {
		user: user,
		load: load,
		search: function(user_id) {
			if (user_id != undefined) {
				var scope = this
				
				console.log("Sending search request to sever");
				$http({
					url: "search_request", 
					method: "GET",
					params: {
						request: "user",
						user_id: user_id,
					},
				}).then(function(response) {
					console.log("Receiving answer")
					scope.load(response.data)
				});
				return true;
			}
			return false;
		},
	};
});