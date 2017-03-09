angular.module("app").controller("TimeStatisticsCtrl", function ($scope, timeStatisticsService) {
	$scope.state = timeStatisticsService;
	timeStatisticsService.generate()
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
				'echarts/chart/line' // require the specific chart type
			],
			function (ec) {
				// Initialize after dom ready
				var myChart = ec.init(document.getElementById('main')); 
				
				var option = {
					tooltip : {
						trigger: 'axis'
					},
					legend: {
						data:['Status','Comment']
					},
					calculable : true,
					xAxis : [
						{
							type : 'category',
							boundaryGap : false,
							data : $scope.state.data.date
						}
					],
					yAxis : [
						{
							type : 'value'
						}
					],
					series : [
						{
							name:'Status',
							type:'line',
							stack: '总量',
							itemStyle: {normal: {areaStyle: {type: 'default'}}},
							data: $scope.state.data.status
						},
						{
							name:'Comment',
							type:'line',
							stack: '总量',
							itemStyle: {normal: {areaStyle: {type: 'default'}}},
							data: $scope.state.data.comment
						},
					]
				};
				// Load data into the ECharts instance 
				myChart.setOption(option); 
			}
		);
	});
})

.service('timeStatisticsService', function($http) {
	var data = {
		date: [],
		status: [],
		comment: [],
	};

	var loading = true;

	var params = {};

	return {
		data: data,
		loading: loading,

		setParams: function(state) {
			params = state;
		},
		generate: function() {
			if (params != undefined) {
				scope = this

				this.loading = true;

				params.request = "timeStatistics";

				console.log("Sending search request to sever");
				$http({
					url: "search_request", 
					method: "GET",
					params: params
				}).then(function(response) {
					console.log("Receiving answer");
					console.log(response.data)
					scope.data = response.data.data;

					scope.loading = false;
				});
				return true;
			}
			return false;
		},
	};
});

