angular.module("app").controller("StatusListVisualisationCtrl", function ($scope, $controller, $uibModal, statusListVisualisationService, statusService, userService) {
	$controller('ListVisualisationCtrl', {$scope: $scope, listVisualisationService: statusListVisualisationService});

	$scope.state = statusListVisualisationService;

	$scope.toggleSave = false;

	$scope.selectStatus = function (status) {
	}

	var allStatusSelected = false;
	$scope.selectAllStatus = function () {
		allStatusSelected = !allStatusSelected;
		for (status in $scope.state.statusList) {
			$scope.state.statusList[status].isSelected = allStatusSelected;
		}
	};

	$scope.saveAsEvent = function() {
		var modalInstance = $uibModal.open({
			animation: true,
			templateUrl: 'saveAsEventModal.html',
			controller: 'SaveAsEventCtrl',
			size: 'lg',
			resolve: {
				statusList: function() {
					return $scope.state.statusList;
				}
			}
		});
	};

	$scope.toJson = function() {
		var modalInstance = $uibModal.open({
			animation: true,
			templateUrl: 'toJsonModal.html',
			controller: 'ToJsonCtrl',
			size: 'lg',
			resolve: {
				statusList: function() {
					return $scope.state.statusList;
				}
			}
		});
	};

	$scope.visualize = function(status) {
		status._source.type = status._type
		if (status.highlight != undefined) {
			if (status.highlight['user_simple.name'] != undefined)
				status._source.user_simple.name = status.highlight['user_simple.name'][0]
			if (status.highlight.text != undefined)
				status._source.text = status.highlight.text[0]
		}
		statusService.load(status._source);
	};

	$scope.visualizeUser = function(id) {
		userService.search(id);
	}
})

.service('statusListVisualisationService', function($http) {
	var page = 1;
	var orderBy = "date";
	var reverse = false;

	var statusList = [];
	var selectedList = [];
	var trueTotalItems = 0;
	var totalItems = 0;

	var loading = true;

	var params = undefined;

	return {
		page: page,
		orderBy: orderBy,
		reverse: reverse,
		statusList: statusList,
		selectedList: selectedList,
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

				params.request = "statusList";
				params.page =  this.page - 1;
				params.orderBy = this.orderBy;
				params.reverse = this.reverse;

				console.log("Sending search request to sever");
				$http({
					url: "search_request", 
					method: "GET",
					params: params
				}).then(function(response) {
					console.log("Receiving answer");
					scope.statusList = formatStatusList(response.data.hits);
					scope.trueTotalItems = response.data.total;
					scope.totalItems = response.data.total< 10000? response.data.total : 10000;
					scope.loading = false;
				});
				return true;
			}
			return false;
		},
	};
})

.controller('SaveAsEventCtrl', function ($scope, $uibModalInstance, statusList) {
	$scope.save = function () {
		$uibModalInstance.close();
	};
})

.controller('ToJsonCtrl', function ($scope, $uibModalInstance, statusList) {
	$scope.fields = [
		{label:'id', isSelected: true},
		{label:'text', isSelected: true},
		{label:'created_at', isSelected: true},
		{label:'geo', isSelected: true},
		{label:'source', isSelected: true},
		{label:'url', isSelected: true},
		{label:'repost_count', isSelected: true},
		{label:'comments_count', isSelected: true},
		{label:'attitude_count', isSelected: true},
		{label:'user.user_id', isSelected: true},
		{label:'user.name', isSelected: true},
		{label:'user.location', isSelected: true},
		{label:'user.follower_counts', isSelected: true},
		{label:'retweeted_status_id', isSelected: true},
		{label:'created_at', isSelected: true},
		{label:'comments', isSelected: true},
		{label:'pic_urls', isSelected: true},
		{label:'bmiddle_pic', isSelected: true},
		{label:'original_pic', isSelected: true},
		{label:'thumbnail_pic', isSelected: true},
		{label:'textLength', isSelected: true},
		{label:'userType', isSelected: true},
		{label:'apiTimestamp', isSelected: true},
		{label:'parserTimestamp', isSelected: true},
		{label:'relevance', isSelected: true},
		{label:'keywords', isSelected: true},
		{label:'feelings', isSelected: true},
		{label:'pertinence', isSelected: true},
		{label:'events', isSelected: true},
		{label:'topic', isSelected: true},
		{label:'mentions', isSelected: true},
		{label:'hashtags', isSelected: true},
	];

	$scope.download = function () {
		downloadList = []
		for (status in statusList) {
			if (statusList[status].isSelected) {
				newStatus = {};
				for (field in $scope.fields) {
					if ($scope.fields[field].isSelected == true)
						newStatus[$scope.fields[field].label] = statusList[status]._source[$scope.fields[field].label];
				}
				downloadList.push(newStatus);
			}
		}
		var file = new Blob([JSON.stringify(downloadList)]);
		saveAs(file,'list.json')

		$uibModalInstance.close();
	};
});

formatStatusList = function(statusList) {
	for (status in statusList) {
		statusList[status].isSelected = false;
	}
	return statusList
}