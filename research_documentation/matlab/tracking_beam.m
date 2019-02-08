%% Construction of tracking beams (TBs)
%
% This script demonstrates how synthesised beams (SBs) need to be combined
% over time to form a tracking beam at a specific point within the
% field-of-view of the compound beam (CB)
%
% SJW, 12 December 2017
%% start with a clean workspace
clear
close all

%% simulation parameters for APERTIF-10 configuration
xpos = (0:1:9).' * 144;           % x-positions of the WSRT dishes in m
ypos = zeros(10, 1);              % y-positions of the WSRT dishes in m
lambda = 0.21;                    % assumed observing wavelength in m
fmax = 1.5e9;                     % maximum frequency in Hz
arcmin2rad = (pi / 180) / 60;     % conversion from arcmin to radian
thetamax = 15 * arcmin2rad;       % maximum distance from CB center in rad
c = 2.99792e8;                    % speed of light in m/s
Bmax = xpos(end) - xpos(1);       % maximum baseline
Bcq = 144;                        % common quotient baseline in m

dl = 5e-5;                        % resolution of (l, m)-grid in m
Tobs = 12 * 3600;                 % duration of observation in s
tstep = 200;                      % time resolution in simulation in s
thetasrc = 6;                     % distance of source from field center
                                    % measured in SB separation
phisrc = pi/3;                    % azimuthal angle of source in rad
omegaE = 2 * pi / (24 * 3600);    % angular velocity of Earth in rad/s

%% construct grid of SBs
lambda_max = c / fmax;            % wavelength at fmax
theta_gr = lambda_max / Bcq;      % distance to grating response at fmax
nofTAB = 12;                      % number of TABs, design parameter
theta_sep_sb = theta_gr / nofTAB; % TAB separation at fmax
Nsynth = 2 * floor(thetamax / theta_sep_sb) + 1;
SBidx = -(Nsynth - 1) / 2:(Nsynth - 1) / 2;

%% define grid for calculation of beam patterns
l = 0:dl:thetamax;
l = [-fliplr(l(2:end)), l];
m = l;
lmdist = sqrt(meshgrid(l).^2 + meshgrid(m).'.^2);
mask = ones(size(lmdist));
mask(lmdist > thetamax) = NaN;

%% example 1 of combining TABs over a 12-hour observation
pbeam1 = zeros(size(lmdist));
for tidx = 0:floor(Tobs/tstep);
    cur_SBidx = round(thetasrc * cos(omegaE * tidx * tstep + phisrc));
    rotangle = ((tidx * tstep) / (24 * 3600)) * 2 * pi;
    rotmat = [cos(rotangle), -sin(rotangle); sin(rotangle), cos(rotangle)];
    pos = [xpos, ypos] * rotmat.';
    lm = rotmat * [cur_SBidx * theta_sep_sb; 0];
    vbeam = xytolm(pos(:, 1), pos(:, 2), eye(10), l, m, lambda, lm(1), lm(2));
    pbeam1 = pbeam1 + abs(vbeam).^2 .* mask;
end
imagesc(l, m, pbeam1);
set(gca, 'FontSize', 16, 'YDir', 'normal');
xlabel('West \leftarrow l \rightarrow East');
ylabel('South \leftarrow m \rightarrow North');
lsrc = sin(thetasrc * theta_sep_sb) * cos(phisrc);
msrc = sin(thetasrc * theta_sep_sb) * sin(phisrc);
title(['\theta = ' num2str(thetasrc * theta_sep_sb * 180 / pi * 60, '%1.2f') ...
       ' arcmin, \phi = ' num2str(phisrc * 180 / pi, '%1.0f') ' degrees']);
