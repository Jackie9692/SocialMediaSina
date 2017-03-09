angular.module("app").controller("SearchStatusCtrl", function ($scope, searchStatusService, statusListVisualisationService, timeStatisticsService, sentimentStatisticsService, locationStatisticsService) {
	$scope.state = searchStatusService;

	var allTopicSelected = true;
	$scope.selectAllTopic = function () {
		allTopicSelected = !allTopicSelected;
		for (topic of $scope.state.topicList) {
			topic.isSeleted = allTopicSelected;
		}
	};

	$scope.search = function () {
		statusListVisualisationService.setParams($scope.state);
	};

	$scope.showTimeStatistics = function () {
		timeStatisticsService.setParams($scope.state);
	};

	$scope.showSentimentStatistics = function () {
		sentimentStatisticsService.setParams($scope.state);
	};

	$scope.showLocationStatistics = function () {
		locationStatisticsService.setParams($scope.state);
	};

	$scope.altInputFormats = ['M!/d!/yyyy'];
})

.service('searchStatusService', function() {
	var keywords = "";
	var location = "";
	var topicList = [
		new Checkbox("Topic 1"),
		new Checkbox("Topic 2"),
	];
	var events = "";
	var mentions = "";
	var hashtags = "";
	var dbList = [
		"raw_data_db",
	];
	var selectedDb = "raw_data_db";
	var date = new Date()
	var timePeriod = {
		from: new Date(date.getFullYear(), date.getMonth()-1, date.getDate(),8), //The 8 is here to hanle the time zone.
		to: new Date(date.getFullYear(), date.getMonth(), date.getDate(),8),
	};
	var source = {
		website: true,
		iphone: true,
		android: true,
		windowsPhone: true,
		others: true,
	};
	var feelings = {
		positive: true,
		neuter: true,
		negative: true,
	};	
	var statusOnly = false;

	return {
		keywords: keywords,
		location: location,
		topicList: topicList,
		events: events,
		mentions: mentions,
		hashtags: hashtags,
		dbList: dbList,
		selectedDb: selectedDb,
		timePeriod: timePeriod,
		source: source,
		feelings: feelings,
		statusOnly: statusOnly,
	};
});

var Checkbox = function (value) {
	this.value = value;
	this.isSelected = true;
	this.click = function() {
		this.isSelected = !this.isSelected;
	};
};