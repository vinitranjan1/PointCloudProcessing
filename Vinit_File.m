function createFixedFile()
File_Name = 'AllentownRoom2.txt';

%Open the raw file
disp('Remember to change the "FC" varible for each file. Reading in Old file...')
xyz1 = openCloud(File_Name);

pc = pointCloud(xyz1);
pc.plot

%Allentown Room 4Sub
FC  = [-24.03            13.45; %TL
       -15.13             8.22; %BL
       -18.84            22.35; %TR
       -9.91             17.18];%BR


[xyz2,How_close_to_90,angleInDegrees] = correctData(xyz1,FC);
disp(strcat('How Close it is to 90 degrees: ', num2str(How_close_to_90)))
disp(strcat('The Angle measures at: ', num2str(angleInDegrees)))
xyz2 = xyz2*39.3701; %in inches

pc = pointCloud(xyz2);
pc.plot
%--------------------------------------------------------------------------

function [xyz,How_close_to_90,angleInDegrees] = correctData(xyz,FC)
Zscale = ZScale(xyz(:,3));
xyz(:,3) = xyz(:,3) + (-Zscale);

%Scale the X and Y axes
FC_correced = FC;
FC_correced(:,1) = FC(:,1)-FC(2,1);
FC_correced(:,2) = FC(:,2)-FC(2,2);

xyz(:,1) = xyz(:,1)-FC(2,1);
xyz(:,2) = xyz(:,2)-FC(2,2);

%create the vectors along the edges
V1 = FC_correced(1,:) - FC_correced(2,:);
V2 = FC_correced(4,:) - FC_correced(2,:);

%find the inner product
inn_prod = dot(V1,V2);

%figure out the rectangly-ness of it 
How_close_to_90 = inn_prod/(norm(V1)*norm(V2));
angleInDegrees = (180/pi) * acos(How_close_to_90); %Retangle corner is 90 degrees?

%find the amount that it needs to be rotated
rotateBy = -atan2(FC_correced(4,2),FC_correced(4,1));

%affine transforms
SCALE = [cos(rotateBy) sin(rotateBy);
        -sin(rotateBy) cos(rotateBy)];
xyz(:,1:2) = xyz(:,1:2)*SCALE;

Xscale = XScale(xyz(:,1));
xyz(:,1) = xyz(:,1) + (-Xscale);

Yscale = YScale(xyz(:,2));
xyz(:,2) = xyz(:,2) + (-Yscale);
%--------------------------------------------------------------------------

function scaling = XScale(pts)
[A,T] = hist(pts,min(pts):0.01:max(pts)); % same as z
pks = findpeaks(A,'MinPeakDistance',50,'MinPeakHeight',1000); % find "first" one and make wall
scaling = T(A == pks(1));
scaling = scaling(1);
%--------------------------------------------------------------------------

function scaling = YScale(pts)
[A,T] = hist(pts,min(pts):0.01:max(pts));
pks = findpeaks(A,'MinPeakDistance',50,'MinPeakHeight',1000);
scaling = T(A == pks(1));
scaling = scaling(1);
%--------------------------------------------------------------------------

function scaling = ZScale(pts)
[A,T] = hist(pts,min(pts):0.01:max(pts)); % bin into increments
[m,ind] = max(A); % get the z value that when binned has highest frequency
scaling = T(ind);
%--------------------------------------------------------------------------

function xyz = openCloud(filename)
fid=fopen(filename,'r');
data=textscan(fid,'%f %f %f %f\n','Delimiter',' ');
fclose(fid);
x3D = cell2mat(data(1));
y3D = cell2mat(data(2));
z3D = cell2mat(data(3));
xyz = [x3D y3D z3D];
%--------------------------------------------------------------------------
