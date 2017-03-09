angular.module("app").controller("LocationStatisticsCtrl", function ($scope, locationStatisticsService) {
	$scope.state = locationStatisticsService;
	locationStatisticsService.generate()
	$scope.$watch("state.loading", function(current, previous) {
		require.config({
		paths: {
			echarts: 'http://echarts.baidu.com/build/dist'
			}
		});

		// use
		require(
			[
				'echarts',
				'echarts/chart/map' // require the specific chart type
			],
			function (ec) {
				// Initialize after dom ready
				var myChart = ec.init(document.getElementById('main')); 
				
				var option = {
					tooltip : {
						trigger: 'item'
					},
					legend: {
						orient: 'vertical',
						x:'left',
						data:['Status','Comment']
					},
					dataRange: {
						min: 0,
						max: $scope.state.max,
						x: 'left',
						y: 'bottom',
						text:['max','min'],           // 文本，默认为数值文本
						calculable : true
					},
					series : [
						{
							name: 'Status',
							type: 'map',
							mapType: 'china',
							roam: false,
							itemStyle:{
								normal:{label:{show:true}},
								emphasis:{label:{show:true}}
							},
							data: $scope.state.statusData
						},
						{
							name: 'Comment',
							type: 'map',
							mapType: 'china',
							itemStyle:{
								normal:{label:{show:true}},
								emphasis:{label:{show:true}}
							},
							data: $scope.state.commentData
						}
					]
				};
				// Load data into the ECharts instance 
				myChart.setOption(option); 
			}
		);
	});
})

.service('locationStatisticsService', function($http) {
	var statusData = [];
	var commentData = [];
	var totalItems = 0;
	var max = 0;

	var loading = true;

	var params = {};

	return {
		totalItems: totalItems,
		statusData: statusData,
		commentData: commentData,
		max: max,
		loading: loading,

		setParams: function(state) {
			params = state;
		},
		generate: function() {
			if (params != undefined) {
				scope = this

				this.loading = true;

				params.request = "locationStatistics";

				console.log("Sending search request to sever");
				$http({
					url: "search_request", 
					method: "GET",
					params: params
				}).then(function(response) {
					console.log("Receiving answer");
					console.log(response.data)
					scope.totalItems = response.data.totalItems;
					scope.statusData = response.data.statusData;
					scope.commentData = response.data.commentData;
					scope.max = response.data.max;
					scope.loading = false;
				});
				return true;
			}
			return false;
		},
	};
});

