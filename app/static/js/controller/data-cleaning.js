angular.module("app").controller("DataCleaningCtrl", function ($scope, $uibModal, dataCleaningService) {
	$scope.state = dataCleaningService;
	dataCleaningService.getTasks();

	$scope.visualizeCleaningTask = function(task) {
		console.log(task)
	}
	$scope.taskModal = function(task) {
		var modalInstance = $uibModal.open({
			animation: true,
			templateUrl: 'new_cleaning_task.html',
			controller: 'TaskModalCtrl',
			size: 'lg',
			resolve: {
				task: function() {
					return task;
				}
			}
		});
	};
})

.service('dataCleaningService', function($http) {
	var taskList = [];
	var hasNoData = true;
	var getTasks = function() {
		scope = this
		this.hasNoData = true;

		console.log("Getting cleaning tasks list");
		$http({
			url: "monitor_cleaning_tasks", 
			method: "GET",
			params: {}
		}).then(function(response) {
			console.log("Receiving cleaning task list");
			scope.taskList = formatTaskList(response.data.taskList);
			if (scope.taskList != false)
				scope.hasNoData = false;
		});
		return true;
	}

	return {
		taskList: taskList,
		hasNoData: hasNoData,
		getTasks: getTasks,
		addTask: function(task) {
			scope = this
			console.log("Adding new data cleaning task");
			$http({
				url: "add_cleaning_task", 
				method: "GET",
				params: {task:task}
			}).then(function(response) {
				console.log("Cleaning task added");
				scope.getTasks();
			});
			return true;
		}
	};
})

.controller('TaskModalCtrl', function ($scope, $uibModalInstance, dataCleaningService, task) {
	if (task == undefined) {
		$scope.isNewTaskModal = true;
		$scope.task = {
			name: null,
			sourceDb: "raw_data_db",
			destinationDb: null,
			cleaningStrategy: "keywords",
			keywords: null,
			taskType: "cyclic",
			taskState: "state",
			cyleStyle: "fixedInterval",
			fixTimeInterval: null,
			specificTime: {
				h: 12,
				m: 0,
				s: 0,
			}
		}
	}
	else {
		$scope.isNewTaskModal = false;
		$scope.task = task;
	}

	$scope.close = function() {
		$uibModalInstance.close();
	}

	$scope.create = function() {
		//Should add some control on the form input
		dataCleaningService.addTask($scope.task)
		$uibModalInstance.close();
	}
});

var formatTaskList = function(taskList) {
	console.log(taskList)
	formatedTaskList = [];
	for (x in taskList) {
		task = taskList[x]
		formatedTaskList.push({
			name: task.name,
			sourceDb: task.source_db,
			destinationDb: task.destination_db,
			cleaningStrategy: task.cleaning_strategy,
			keywords: task.keywords,
			taskType: task.task_type,
			taskState: task.task_state,
			cycleType: task.cycle_type,
			fixTimeInterval: task.interval_minutes,
			createdTime: task.displayed_created_time,
			specificTime: task.specific_time[0] != undefined ? {
				h: task.specific_time[0].hour,
				m: task.specific_time[0].minute,
				s: task.specific_time[0].second,
			} : null
		})
	}
	return formatedTaskList
}