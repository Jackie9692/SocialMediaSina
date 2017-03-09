angular.module("app").controller("SearchUserCtrl", function ($scope, searchUserService, userListVisualisationService) {
	$scope.state = searchUserService;

	$scope.search = function () {
		userListVisualisationService.setParams($scope.state);
	};
})

.service('searchUserService', function() {
	var name = "";
	var location = "";
	var greaterThan = true;
	var followers = 0;
	var rate = {
		minValue: 0,
		maxValue: 100,
		options: {
			floor: 0,
			ceil: 100,
			step: 5,
			vertical: true
		}
	};
	var category = {
		enterpriseIsSelected: true,
		weMediaIsSelected: true,
		industryAllianceIsSelected: true,
		popularNewsMediaIsSelected: true,
		normalIsSelected: true,
	};
	var gender = "both";
	return {
		name: name,
		location: location,
		greaterThan: greaterThan,
		followers: followers,
		rate: rate,
		category: category,
		gender: gender,
	};
});