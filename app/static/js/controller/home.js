angular.module("app").controller("HomeCtrl", function ($scope, homeService, statusService, userService) {
	$scope.state = homeService;
	homeService.generate()

	var retrieveGoal = 50000;

	$scope.visualize = function(status) {
		status.type = "status"
		statusService.load(status);
	};

	$scope.visualizeUser = function(id) {
		userService.search(id);
	}

	$scope.$watch("state.loading", function(current, previous) {
		require.config({
		paths: {
			echarts: 'http://echarts.baidu.com/build/dist'
			}
		});

		// dashboard
		require(
			[
				'echarts',
				'echarts/chart/gauge' // require the specific chart type
			],
			function (ec) {
				// Initialize after dom ready
				var myChart = ec.init(document.getElementById('dashboard'));
				
				var option = {
					series : [
						{
							name:'',
							type:'gauge',
							detail : {formatter:'{value}%'},
							data:[{value: Math.round($scope.state.pastMonthTotalRetrieved / retrieveGoal * 100), name: ''}]
						}
					]
				};
				// Load data into the ECharts instance 
				myChart.setOption(option); 
			}
		);

		//Topic Pie
		require(
			[
				'echarts',
				'echarts/chart/pie' // require the specific chart type
			],
			function (ec) {
				// Initialize after dom ready
				var myChart = ec.init(document.getElementById('topicPie')); 
				
				var option = {
					legend: {
						orient : 'vertical',
						x : 'right',
						data: $scope.state.pastMonthTopics
					},
					calculable : true,
					series : [
						{
							name:'',
							type:'pie',
							radius : ['50%', '70%'],
							itemStyle : {
								normal : {
									label : {
										show : false
									},
									labelLine : {
										show : false
									}
								},
								emphasis : {
									label : {
										show : true,
										position : 'center',
										formatter : "{b}\n{d}%",
										textStyle : {
											fontSize : '30',
											fontWeight : 'bold'
										}
									}
								}
							},
							data: $scope.state.pastMonthTopics
						}
					]
				};
				// Load data into the ECharts instance 
				myChart.setOption(option); 
			}
		);
	});
})

.service('homeService', function($http) {
	var pastMonthTotalRetrieved = 0;

	var pastMonthTopics = [];

	var statusList = [];

	var loading = true;

	var params = {};

	return {
		pastMonthTotalRetrieved: pastMonthTotalRetrieved,
		pastMonthTopics: pastMonthTopics,
		statusList: statusList,

		loading: loading,

		setParams: function(state) {
			params = state;
		},

		generate: function() {
			if (params != undefined) {
				scope = this

				this.loading = true;

				params.request = "homeStatistics";

				console.log("Sending search request to sever");
				$http({
					url: "search_request", 
					method: "GET",
					params: params
				}).then(function(response) {
					console.log("Receiving answer");
					console.log(response.data);
					scope.pastMonthTotalRetrieved = response.data.pastMonthTotalRetrieved;
					scope.statusList = response.data.lastStatusRetrieved;
					scope.pastMonthTopics = response.data.pastMonthTopics;
					
					scope.loading = false;
				});
				return true;
			}
			return false;
		},
	};
});

