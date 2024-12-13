% Define the base URL of the Flask API
baseUrl = 'http://127.0.0.1:5000/simulate';

% Define the parameters to be sent
params = struct('users', 2, 'duration', 120, 'rate', 24, 'print_output', 2);

% Create the query string
queryString = sprintf('?users=%d&duration=%d&rate=%f&print_output=%s', ...
                      params.users, params.duration, params.rate, params.print_output);

% Create the full URL with the query parameters
url = strcat(baseUrl, queryString);

% Send an HTTP GET request to the Flask API
response = webread(url);

% Display the response from the Flask API
disp(response.result);
