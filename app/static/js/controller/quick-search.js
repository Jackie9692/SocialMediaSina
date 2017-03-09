angular.module("app").controller("QuickSearchCtrl", function ($scope, quickSearchService, statusListVisualisationService) {
	
	$scope.state = quickSearchService;
	$scope.visualisationURL = ($scope.state.keywords != "") ? "status_list_visualisation" : undefined;

	$scope.search = function () {
		if ($scope.state.keywords != "") {
			statusListVisualisationService.setParams($scope.state);
			statusListVisualisationService.search();
		}
		$scope.visualisationURL = "status_list_visualisation";
	};
})

.service('quickSearchService', function() {
	var keywords = "";

	return {
		keywords: keywords,
	};
});