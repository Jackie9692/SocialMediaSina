angular.module("app").controller('ListVisualisationCtrl', function($scope, listVisualisationService) {

	//params
	$scope.itemsPerPage = 50;
	$scope.maxSize = 9;

	$scope.$watch("state.page", function(page, previousPage) {
		$scope.noResults = !listVisualisationService.search();

		$scope.next.isDisabled = ($scope.state.totalItems != 0 && page >= $scope.state.totalItems / $scope.itemsPerPage) ? true : false;
		$scope.previous.isDisabled = (page <= 1) ? true : false;
	});

	$scope.orderBy = function(value) {
		$scope.state.orderBy = value;
		$scope.state.reverse = !$scope.state.reverse;
		$scope.noResults = !listVisualisationService.search();
	};

	$scope.next = {
		click: function() {
			if ($scope.state.page < $scope.state.totalItems / $scope.itemsPerPage)
				$scope.state.page++;
		},
		isDisabled: false,
	};

	$scope.previous = {
		click: function() {
			if ($scope.state.page > 1)
				$scope.state.page--;
		},
		isDisabled: false,
	};
});