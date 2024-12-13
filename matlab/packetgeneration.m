% 802.11 MAC Frame Generation
% Create a MAC frame configuration object for a Data frame
dataCfg = wlanMACFrameConfig('FrameType', 'Data');
disp(dataCfg);

% Configure the frame header fields
dataCfg.FromDS = 1;  % From DS flag
dataCfg.ToDS = 0;    % To DS flag
dataCfg.Address1 = 'FCF8B0102001'; % Receiver address
dataCfg.Address2 = 'FCF8B0102002'; % Transmitter address
dataCfg.Address3 = 'FCF8B0102003'; % Address3 field

% Create a 1500-byte payload with random data
payload = repmat('11', 1, 1500);  % 1500 bytes of random data

% Generate the Data frame as octets
dataFrame = wlanMACFrame(payload, dataCfg);
disp('Data Frame (octets):');
disp(dataFrame);

% Define the URL of the Flask server endpoint
url = 'http://localhost:5000/upload';

% Set options for the HTTP POST request
options = weboptions('MediaType', 'application/octet-stream');

% Send the binary data directly to the Flask server
response = webwrite(url, dataFrame, options);

% Display the server's response
disp('Server response:');
disp(response);
