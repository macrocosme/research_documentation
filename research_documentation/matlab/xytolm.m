function signal = xytolm(x, y, gain, l, m, lambda, l0, m0)
  % calculates voltage beam
  % if l==l0 and m==m0,
  %   signal has size 1 x 1 x length(l0) x length(m0) and
  %   contains the main beam sensitivity on these locations
  % otherwise
  %   signal has size length(l)
  %   and contains complete beam patterns
  % beam directions on the grid defined
  %   x length(m) * length(l0) * length(m0)
  %     on a grid defined by l and m for main by l0 and m0
  if (isequal(l, l0) && isequal(m, m0))
    [l0grid, m0grid] = meshgrid(l0, m0);
    signal = zeros(length(l0grid(:)), 1);
    for idx = 1:length(l0grid(:));
      disp(['working on ' num2str(idx) ' of ' num2str(length(l0grid(:)))]);
      xsrcdelay = -x(:) * l0grid(idx);
      ysrcdelay = -y(:) * m0grid(idx);
      arrayvec0 = exp(-2 * pi * i * (xsrcdelay + ysrcdelay) / lambda);
      arrayvec = gain * arrayvec0;
      norm = sqrt(sum(abs(arrayvec).^2));
      signal(idx) = arrayvec0' * arrayvec / norm;
    end
    signal = reshape(signal, [length(l0), length(m0)]);
  else
    %[l0grid, m0grid] = meshgrid(l0, m0);
    xsrcdelay = -x(:) * l0(:).';
    ysrcdelay = -y(:) * m0(:).';
    arrayvec = gain * exp(-2 * pi * i * (xsrcdelay + ysrcdelay) / lambda); norm = sqrt(sum(abs(arrayvec).^2));
    Wx = exp(-2 * pi * i * l(:) * x(:).' / lambda);
    Wy = exp(-2 * pi * i * m(:) * y(:).' / lambda);
    %W = khatrirao(Wx, Wy);
    W = kr(Wx, Wy);
    signal = W * arrayvec * diag(1 ./ norm);
    signal = reshape(signal, [length(l), length(m), length(l0)]);
  end
