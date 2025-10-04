% bee_detection.m

% image_dir = './images';
% background_image = 'images/image_2025-03-24_08-46-13.jpg';

image_dir = './images2';
background_image = 'images2/image_2025-02-25_15-05-32.jpg';

% 메인 실행부
[img, hsv] = preprocessImage(background_image, 800);
mask = detectWhitePanel(hsv);

% 가장 큰 컨투어 찾기
stats = regionprops(mask, 'Area', 'BoundingBox');
if isempty(stats)
    error('No white panel found.');
end
[~, idxMax] = max([stats.Area]);
bb = stats(idxMax).BoundingBox;  % [x, y, width, height]
roiCoords = round(bb);
% ROI 추출
x=roiCoords(1); y=roiCoords(2);
w=roiCoords(3); h=roiCoords(4);

% 배경(그레이스케일 ROI)
roiColor = img(y:y+h-1, x:x+w-1, :);
background = rgb2gray(roiColor);

% 디렉토리 내 모든 이미지 처리
processImages(image_dir, roiCoords, background);


function [img, hsv] = preprocessImage(imagePath, targetWidth)
    img = imread(imagePath);
    img = resizeWithAspectRatio(img, targetWidth, []);
    hsv = rgb2hsv(img);
end

function out = resizeWithAspectRatio(img, width, height)
    [h, w, ~] = size(img);
    if isempty(width) && isempty(height)
        out = img;
        return;
    end
    if ~isempty(width)
        scale = width / w;
    else
        scale = height / h;
    end
    out = imresize(img, scale);
end

function mask = detectWhitePanel(hsv)
    % HSV 채널 스케일 조정
    H = hsv(:,:,1) * 360;
    S = hsv(:,:,2) * 255;
    V = hsv(:,:,3) * 255;
    
    % 흰색 임계치
    mask = (V >= 200) & (S <= 50);
    
    % 형태학적 연산: 닫기 → 열기 → 침식
    se = strel('rectangle',[15 15]);
    mask = imclose(mask, se);
    mask = imopen(mask, se);
    mask = imerode(mask, se);
end

function processImages(imageDir, roiCoords, background)
    % 이미지 파일 목록 가져오기
    exts = {'.jpg','.png','.bmp','.tif','.jpeg'};
    D = dir(fullfile(imageDir,'*'));
    files = {};
    for k=1:numel(D)
        [~,~,ext] = fileparts(D(k).name);
        if ismember(lower(ext), exts)
            files{end+1} = D(k).name; %#ok<AGROW>
        end
    end
    
    idx = 1;
    fig = figure('Name','Detected ROI','NumberTitle','off');
    fig2 = figure('Name','fourier','NumberTitle','off');
    while true
        fname = files{idx};
        I = imread(fullfile(imageDir, fname));
        I = resizeWithAspectRatio(I, 800, []);
        Igray = rgb2gray(I);
        
        % ROI 추출
        x=roiCoords(1); y=roiCoords(2);
        w=roiCoords(3); h=roiCoords(4);
        targetROI = Igray(y:y+h-1, x:x+w-1);
        
        % 차 분할 → 형태학적 필터 → Otsu
        diffImg = imabsdiff(background, targetROI);
        se2 = strel('disk',2);
        filt = imopen(diffImg, se2);
        level = graythresh(filt);
        bw = imbinarize(filt, level);

        % 2) 서브플롯으로 4개 영상 표시
        figure(fig); clf;
        subplot(2,2,1)

        imshow(I); hold on
        rectangle('Position',[x y w h],'EdgeColor','g','LineWidth',2);
        beeCount = 0;
        if level*255 >= 30
            stats2 = regionprops(bw, 'BoundingBox');
            beeCount = length(stats2);
            for s = stats2'
                bb2 = s.BoundingBox;
                rectangle('Position',[x+bb2(1) y+bb2(2) bb2(3) bb2(4)], ...
                          'EdgeColor','r','LineWidth',2);
            end
        end
        t = sprintf("%s, %d", fname, beeCount);
        title(t,'Interpreter','none','Color','w','BackgroundColor','k');
        hold off

        subplot(2,2,2)
        imshow(diffImg)
        title('Difference')

        subplot(2,2,3)
        imshow(filt)
        title('Filtered Difference')

        subplot(2,2,4)
        imshow(bw)
        title(sprintf('Otsu Threshold (level=%d)', level*255))
        
        figure(fig2); clf;
        subplot(2,1,1)
        cf = fftshift(fft2(bw));
        cf = log(1 + abs(cf));
        fm = max(cf(:));
        imshow(uint8(cf/fm));


        % 키 입력 처리: Esc(27)=종료, a=이전, d=다음
        wbp = waitforbuttonpress;
        key = get(fig, 'CurrentCharacter');
        key2 = get(fig2, 'CurrentCharacter');
        if key == ""
            key = key2;
        end
        if key == char(27)
            break
        elseif key=='a' && idx>1
            idx = idx - 1;
        elseif key=='d' && idx<numel(files)
            idx = idx + 1;
        end
    end
    close(fig);
end