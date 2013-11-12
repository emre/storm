function Storm($scope, $http) {

  $scope.version = "1.0";
  $scope.state = {
    action: "add new",
    filter: false,
    position: localStorage.getItem("position") == "top" ? "top" : ""
  };

  function urify(username, hostname, port) {
    return (username ? username + "@" : "") + (hostname || "<no host>") + (port? ":" + port : "");
  }

  function fetch(callback) {
    $http.get("/list").success(function (data) {
      $scope.servers = data.map(function (host) {
        var port = host.options.port;
        var hostname = host.options.hostname;
        var username = host.options.user;
        host.uri = urify(username, hostname, port);
        host.params = Object.keys(host.options).map(function (option) {
          return option + ": " + host.options[option];
        }).join(", ");
        return host;
      });
      if (callback) callback();
    });
  }

  function plural() {
    $scope.servers.plural = $scope.servers.length > 1 ? "s" : "";
  }

  function focus() {
    var title = document.getElementById("title");
    title.focus();
    title.select();
  }

  $scope.save = function () {

    if (!$scope.title || !$scope.uri) {
       alert("you must fill all fields!");
       return focus();
    }

    var search = $scope.servers.filter(function (server, index) {
      if ($scope.state.editIndex > -1 && $scope.title == server.title) {
        return true;
      } else {
        return $scope.title == server.title;
      }
    }).length;
    if (search > 0) {
      alert("you already have an entry for this server!");
      return focus();
    }


    if ($scope.state.editIndex > -1) {
      $http.put('/edit', JSON.stringify({name: $scope.title, connection_uri: $scope.uri})).
        success(function(data, status) {
          if (status == 200) {
            $scope.servers[$scope.state.editIndex] = {
              name: $scope.title,
              connection_uri: $scope.uri
            }
            $scope.title = $scope.uri = "";
            $scope.state.editIndex = -1;
            $scope.state.action = "add new";
            $scope.reset();
            focus();
            fetch();
          } else {
            alert("something wrong...");
          }
        }).error(function () {
          alert("something wrong...");
        });
    } else {
      $http.post('/add', JSON.stringify({name: $scope.title, connection_uri: $scope.uri})).
        success(function (data, status) {
          if (status == 201) {
            $scope.servers.push({
              title: $scope.title,
              uri: $scope.uri
            });
            plural();
            $scope.title = $scope.uri = "";
            $scope.state.action = "add new";
            focus();
            fetch();
          } else {
            alert("something wrong...");
          }
        }).error(function () {
          alert("something wrong...");
        });
    }
  };

  $scope.reset = function () {
    $scope.servers = $scope.servers.map(function (server) {
      server.editing = false;
      return server;
    });
    plural();
  };

  $scope.toggleTop = function () {
    var current = $scope.state.position;
    var next = current == "top" ? "bottom" : "top";
    localStorage.setItem("position", next);
    $scope.state.position = next;
  };

  $scope.filtered = function (index, filter) {
    if (!filter) return true;
    if (filter && filter.length == 0) return false;
    return $scope.servers[index].title.indexOf(filter) > -1
        || $scope.servers[index].uri.indexOf(filter) > -1;
  };

  $scope.edit = function (server, index) {
    $scope.state.editIndex = index;
    $scope.state.action = "edit " + server.host;
    $scope.title = server.host;
    $scope.uri = urify(server.options.username, server.options.hostname, server.options.port);
    $scope.reset();
    server.editing = true;
    focus();
  };

  $scope.delete = function (serverToDelete) {
    $http.post("/delete", JSON.stringify({name: serverToDelete.host})).
      success(function () {
        fetch(function () {
          plural();
          $scope.title = $scope.uri = "";
          $scope.reset();
        });
      })
  };

  $scope.servers = [];
  fetch();

  $scope.reset();
}