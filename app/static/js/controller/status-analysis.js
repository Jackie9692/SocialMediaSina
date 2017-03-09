angular.module("app").controller("StatusAnalysisCtrl", function ($scope, $uibModal, statusService, userService, statusListVisualisationService) {
	$scope.status = statusService.status;

	$scope.visualizeUser = function() {
		userService.search($scope.status.user_simple.user_id);
	}

	$scope.visualizeInReplyOf = function() {
		userService.search($scope.status.in_reply_of_id);
	}
	$scope.search = function(arg) {
		statusListVisualisationService.setParams({
			"status_id": $scope.status.status_id,
			"getComments": arg
		});
	}



	$scope.text = 'yolo'
	$scope.open = function () {
		var modalInstance = $uibModal.open({
			animation: true,
			templateUrl: 'myModalContent.html',
			controller: 'ModalInstanceCtrl',
			size: 'lg',
			resolve: {
				text: function () {
					return $scope.status.text;
				}
			}
		});
	};
})

.controller('ModalInstanceCtrl', function ($scope, $uibModalInstance, text, $http) {
	$scope.loading = true;

	$scope.text = text

	params = {
		request: "geolocation",
		text: $scope.text
	}

	console.log("Sending search request to sever");
	$http({
		url: "search_request", 
		method: "GET",
		params: params
	}).then(function(response) {
		console.log("Receiving answer")
		$scope.geolocation = response.data
		$scope.loading = false;
	});

	$scope.ok = function () {
		$uibModalInstance.close();
	};
})

.service('statusService', function() {
	var status = undefined;
	/*status = {
		type: "Status",
		text: "Some nice text here about 电梯",
		user_simple: {
			name: '名字',
			location: '上海'
		},
		created_at: "2016-04-22-T09:03:00",
		source: "IPhone 6",
		repost_count: 42,
		comments_count: 384,
		attitudes_count: 28,
		keywords: ['电梯'],
		sentimentScore: 87,
		pertinence: 50,
	}*/

    return {
    	status: status,
    	load: function(status) {
    		console.log(status.type)
    		if (status.type == undefined)
    			status.type = "Unknown";
    		else
    			status.type = status.type == "status" ? "Status": "Comment";
			if (status.source == undefined)
				status.source = "Unknown";
			if (status.repost_count == undefined)
				status.repost_count = "Unknown";
			if (status.comments_count == undefined)
				status.comments_count = "Unknown";
			if (status.attitudes_count == undefined)
				status.attitudes_count = "Unknown";
			if (status.keywords == undefined)
				status.keywords = "";
			if (status.sentimentScore == undefined)
				status.sentimentScore = -1;
			else
				status.sentimentScore = Math.round(status.sentimentScore*100)
			if (status.sentimentScore == 100)
				status.sentimentScore = 99
			if (status.pertinence == undefined)
				status.pertinence = 50;
			if (status.events == undefined)
				status.events = [];
			if (status.topic == undefined)
				status.topic = "";

    		this.status = status;
    	},
    };
});