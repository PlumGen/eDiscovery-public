import React, { useState } from "react";
import { Tooltip } from 'react-tooltip';
//import 'react-tooltip/dist/react-tooltip.css';
import './markettoolstips.css';

const MarketTools = (props) => {
	
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [tooltipContent, setTooltipContent] = useState("");
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

	const handleMouseEnter = (e, content) => {
	  setTooltipContent(content);
	  setTooltipPosition({ x: e.pageX, y: e.pageY });
	  setTooltipVisible(true);
	};

  const handleMouseLeave = () => {
    setTooltipVisible(false);
  };
  
return (
<>

  <svg
    xmlns="http://www.w3.org/2000/svg"
    xmlnsXlink="http://www.w3.org/1999/xlink"
      viewBox="0 0 857.205 568.693"
      preserveAspectRatio="xMidYMid meet"
      width="100%"
      height="auto"
    {...props}
  >
    <defs>
      <style>{"*{stroke-linejoin:round;stroke-linecap:butt}"}</style>
    </defs>
    <g id="figure_1">
      <path
        id="patch_1"
        d="M0 568.8h857.205V0H0z"
        style={{
          fill: "#fff",
        }}
      />
      <g id="axes_1">
        <path
          id="patch_2"
          d="M28.461 561.6h821.544V7.2H28.461z"
          style={{
            fill: "#fff",
          }}
        />
        <g id="matplotlib.axis_1">
          <g id="xtick_1">
            <path
              id="line2d_1"
              d="M28.461 561.6V7.2"
              clipPath="url(#p4433d6cd14)"
              style={{
                fill: "none",
                strokeDasharray: "2.96,1.28",
                strokeDashoffset: 0,
                stroke: "#ccc",
                strokeOpacity: 0.5,
                strokeWidth: 0.8,
              }}
            />
          </g>
          <g id="xtick_2">
            <path
              id="line2d_3"
              d="M106.704 561.6V7.2"
              clipPath="url(#p4433d6cd14)"
              style={{
                fill: "none",
                strokeDasharray: "2.96,1.28",
                strokeDashoffset: 0,
                stroke: "#ccc",
                strokeOpacity: 0.5,
                strokeWidth: 0.8,
              }}
            />
          </g>
          <g id="xtick_3">
            <path
              id="line2d_5"
              d="M302.31 561.6V7.2"
              clipPath="url(#p4433d6cd14)"
              style={{
                fill: "none",
                strokeDasharray: "2.96,1.28",
                strokeDashoffset: 0,
                stroke: "#ccc",
                strokeOpacity: 0.5,
                strokeWidth: 0.8,
              }}
            />
          </g>
          <g id="xtick_4">
            <path
              id="line2d_7"
              d="M537.036 561.6V7.2"
              clipPath="url(#p4433d6cd14)"
              style={{
                fill: "none",
                strokeDasharray: "2.96,1.28",
                strokeDashoffset: 0,
                stroke: "#ccc",
                strokeOpacity: 0.5,
                strokeWidth: 0.8,
              }}
            />
          </g>
          <g id="xtick_5">
            <path
              id="line2d_9"
              d="M654.4 561.6V7.2"
              clipPath="url(#p4433d6cd14)"
              style={{
                fill: "none",
                strokeDasharray: "2.96,1.28",
                strokeDashoffset: 0,
                stroke: "#ccc",
                strokeOpacity: 0.5,
                strokeWidth: 0.8,
              }}
            />
          </g>
          <g id="xtick_6">
            <path
              id="line2d_11"
              d="M693.52 561.6V7.2"
              clipPath="url(#p4433d6cd14)"
              style={{
                fill: "none",
                strokeDasharray: "2.96,1.28",
                strokeDashoffset: 0,
                stroke: "#ccc",
                strokeOpacity: 0.5,
                strokeWidth: 0.8,
              }}
            />
          </g>
        </g>
        <g id="matplotlib.axis_2">
          <g
            id="text_1"
            style={{
              fill: "#262626",
            }}
            transform="matrix(0 -.12 -.12 0 15.936 360.26)"
          >
            <defs>
              <path
                id="ArialMT-43"
                d="m3763 1606 606-153q-191-747-686-1139T2472-78q-741 0-1205 301-464 302-706 874T319 2325q0 716 273 1248 274 533 778 809 505 277 1111 277 688 0 1156-350 469-350 654-984l-597-141q-160 500-463 728-303 229-762 229-528 0-883-254-355-253-499-680-143-426-143-879 0-584 170-1020t529-652q360-215 779-215 509 0 862 293 354 294 479 872z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-6f"
                d="M213 1659q0 922 512 1366 428 369 1044 369 684 0 1118-449 435-448 435-1239 0-640-192-1008-192-367-560-570-367-203-801-203-697 0-1127 447-429 447-429 1287zm578 0q0-637 278-954t700-317q419 0 697 318 278 319 278 972 0 616-280 933t-695 317q-422 0-700-316-278-315-278-953z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-73"
                d="m197 991 556 87q47-334 261-512t599-178q387 0 574 157 188 158 188 371 0 190-166 300-115 75-575 190-618 157-857 271t-363 315q-123 202-123 446 0 221 101 410 102 190 277 315 131 96 357 163 227 68 487 68 390 0 685-113 296-112 436-305 141-192 194-513l-550-75q-37 256-217 399-180 144-508 144-387 0-553-128t-166-300q0-109 69-197 69-90 216-150 84-31 497-143 597-160 832-262 236-101 370-295 135-193 135-481 0-281-164-530-164-248-474-384-309-136-699-136-647 0-986 269T197 991z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-74"
                d="m1650 503 81-497q-237-50-425-50-306 0-475 97-168 97-237 255t-69 664v1909H113v438h412v822l559 337V3319h566v-438h-566V941q0-241 30-310 30-68 97-109t192-41q94 0 247 22z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-28"
                d="M1497-1347Q1031-759 709 28 388 816 388 1659q0 744 240 1425 281 791 869 1575h403q-378-650-500-928-191-431-300-900-134-584-134-1175 0-1503 934-3003h-403z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-6d"
                d="M422 0v3319h503v-466q156 244 415 392 260 149 591 149 369 0 605-153t333-428q394 581 1025 581 494 0 759-274 266-273 266-842V0h-560v2091q0 337-55 485-54 149-198 239-143 91-337 91-350 0-582-233-231-232-231-745V0h-562v2156q0 375-138 562-137 188-450 188-237 0-439-125-201-125-292-366-91-240-91-693V0H422z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-70"
                d="M422-1272v4591h512v-431q182 253 410 379 228 127 553 127 425 0 750-219t490-618q166-398 166-873 0-509-183-917-182-408-531-625-348-217-733-217-281 0-505 119-223 119-367 300v-1616H422zm509 2913q0-641 259-947 260-306 629-306 375 0 642 317t267 983q0 634-261 949-261 316-623 316-360 0-637-336-276-336-276-976z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-75"
                d="M2597 0v488Q2209-75 1544-75q-294 0-549 112-254 113-378 283-123 171-173 418-35 165-35 525v2056h563V1478q0-440 34-594 53-221 225-348t425-127q253 0 475 130t314 353q93 224 93 649v1778h562V0h-503z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-65"
                d="m2694 1069 581-72q-137-509-509-791-372-281-950-281-728 0-1155 448-427 449-427 1258 0 838 431 1300 432 463 1119 463 666 0 1088-453t422-1275q0-50-3-150H816q31-547 309-838 278-290 694-290 309 0 528 162 219 163 347 519zM847 1978h1853q-37 419-212 628-269 325-697 325-388 0-652-259t-292-694z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-2b"
                d="M1603 741v1256H356v525h1247v1247h531V2522h1247v-525H2134V741h-531z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-45"
                d="M506 0v4581h3313v-540H1113V2638h2534v-538H1113V541h2812V0H506z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-6c"
                d="M409 0v4581h563V0H409z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-79"
                d="m397-1278-63 528q185-50 322-50 188 0 300 63 113 62 185 174 53 85 172 419 15 47 50 138L103 3319h606l691-1922q134-366 241-769 97 388 231 756l709 1935h563L1881-56q-203-547-315-753-150-279-344-408-194-130-463-130-162 0-362 69z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-29"
                d="M791-1347H388q934 1500 934 3003 0 588-134 1166-107 469-297 900-122 281-503 937h403q587-784 868-1575 241-681 241-1425 0-843-324-1631-323-787-785-1375z"
                transform="scale(.01563)"
              />
            </defs>
            <use xlinkHref="#ArialMT-43" />
            <use xlinkHref="#ArialMT-6f" x={72.217} />
            <use xlinkHref="#ArialMT-73" x={127.832} />
            <use xlinkHref="#ArialMT-74" x={177.832} />
            <use xlinkHref="#ArialMT-20" x={205.615} />
            <use xlinkHref="#ArialMT-28" x={233.398} />
            <use xlinkHref="#ArialMT-43" x={266.699} />
            <use xlinkHref="#ArialMT-6f" x={338.916} />
            <use xlinkHref="#ArialMT-6d" x={394.531} />
            <use xlinkHref="#ArialMT-70" x={477.832} />
            <use xlinkHref="#ArialMT-75" x={533.447} />
            <use xlinkHref="#ArialMT-74" x={589.063} />
            <use xlinkHref="#ArialMT-65" x={616.846} />
            <use xlinkHref="#ArialMT-20" x={672.461} />
            <use xlinkHref="#ArialMT-2b" x={700.244} />
            <use xlinkHref="#ArialMT-20" x={758.643} />
            <use xlinkHref="#ArialMT-45" x={786.426} />
            <use xlinkHref="#ArialMT-6d" x={853.125} />
            <use xlinkHref="#ArialMT-70" x={936.426} />
            <use xlinkHref="#ArialMT-6c" x={992.041} />
            <use xlinkHref="#ArialMT-6f" x={1014.258} />
            <use xlinkHref="#ArialMT-79" x={1069.873} />
            <use xlinkHref="#ArialMT-65" x={1119.873} />
            <use xlinkHref="#ArialMT-65" x={1175.488} />
            <use xlinkHref="#ArialMT-29" x={1231.104} />
          </g>
        </g>
        <path
          id="patch_3"
          d="M28.461 561.6V7.2h78.243v554.4z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#fff",
            opacity: 0.2,
            stroke: "#fff",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_4"
          d="M106.704 561.6V7.2h195.605v554.4z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#fff",
            opacity: 0.2,
            stroke: "#fff",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_5"
          d="M302.31 561.6V7.2h234.726v554.4z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#fff",
            opacity: 0.2,
            stroke: "#fff",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_6"
          d="M537.036 561.6V7.2h117.363v554.4z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#fff",
            opacity: 0.2,
            stroke: "#fff",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_7"
          d="M654.4 561.6V7.2h39.12v554.4z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#fff",
            opacity: 0.2,
            stroke: "#fff",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_8"
          d="M693.52 561.6V7.2h156.485v554.4z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#fff",
            opacity: 0.2,
            stroke: "#fff",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_9"
          d="M28.461 492.3h195.606V423H28.46z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#c05746",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
  onMouseEnter={(e) =>
    handleMouseEnter(
      e,
  "<strong>Keyword Search</strong>\n"+
  "\n"+	  
  "<strong>Description</strong>: Relies on manually entered search terms to retrieve documents containing specific words or phrases.\n" +
  "<strong>Drawbacks</strong>:\n"+ 
  "- High false negative rate (missing relevant documents not matching exact terms).\n" +
  "- Labor-intensive and prone to human bias."

    )
  }
  onMouseLeave={handleMouseLeave}			  
        />
        <path
          id="patch_10"
          d="M106.704 423H321.87v-69.3H106.704z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#c59000",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
  onMouseEnter={(e) =>
    handleMouseEnter(
      e,
      "<strong>Conceptual Search</strong>\n"+
	  "\n"+
		"<strong>Description:</strong>\n"+
		"Uses semantic analysis (e.g., topic modeling, latent semantic indexing) to retrieve documents based on conceptual similarity rather than exact keywords.\n"+
		"<strong>Drawbacks</strong>:\n"+ 

		"- Quality depends on training data and algorithms.\n"+
		"- May retrieve documents too loosely related, increasing noise.\n"
	  
    )
  }
  onMouseLeave={handleMouseLeave}		  
        />
        <path
          id="patch_11"
          d="M615.278 423h78.242v-69.3h-78.242z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#c59000",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_12"
          d="M106.704 215.1H321.87v-69.3H106.704z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#90ee90",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
  onMouseEnter={(e) =>
    handleMouseEnter(
      e,
      "<strong>Supervised ML</strong>\n"+
	  "\n"+
		"<strong>Description</strong>:\n"+
		"Uses a labeled training set (human-coded) to train a classifier that ranks the relevance of documents.\n"+

		"<strong>Drawbacks</strong>:\n"+

		"- Requires substantial upfront manual review to train.\n"+
		"- Performance highly dependent on quality and representativeness of the seed set.\n"+
		"- Static: model performance plateaus and doesn’t improve with reviewer feedback.\n"
	  
    )
  }
  onMouseLeave={handleMouseLeave}		  
        />
        <path
          id="patch_13"
          d="M106.704 284.4h293.408v-69.3H106.704z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#f7f7f7",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
  onMouseEnter={(e) =>
    handleMouseEnter(
      e,
      "<strong>Continuous Active Learning (CAL)</strong>\n"+
	  "\n"+
		"<strong>Description:</strong>\n"+
		"An iterative approach where the system continuously retrains the model based on reviewer feedback, prioritizing high-yield documents.\n"+
		"<strong>Drawbacks</strong>:\n"+
		"- Performance can be unpredictable if early documents mislead the model.\n"+
		"- Struggle with rare or nuanced relevance criteria.\n"+
		"- Retrieve documents too loosely related, increasing noise.\n"
	  
    )
  }
  onMouseLeave={handleMouseLeave}			  
        />
        <path
          id="patch_14"
          d="M615.278 284.4h78.242v-69.3h-78.242z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#f7f7f7",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_15"
          d="M28.461 145.8h234.727V76.5H28.461z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#add8e6",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
    onMouseEnter={(e) =>
    handleMouseEnter(
      e,
      "<strong>GenAI</strong>\n"+
	  "\n"+
	"<strong>Description</strong>:\n"+
	"Uses large language models to generate summaries, answer questions, or surface insights directly from documents.\n"+

	"<strong>Drawbacks</strong>:\n"+
	"- Risk of hallucinations or factual inaccuracies.\n"+
	"- Limited explainability—hard to trace how answers are derived.\n"+
	"- Expensive in terms of compute; often not well-audited for legal defensibility.\n"+
	"- Unpredictable performance and results are often not repeatable.\n"
	  
    )
  }
  onMouseLeave={handleMouseLeave}			  
        />
        <path
          id="patch_16"
          d="M693.52 145.8h156.485V76.5H693.52z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#add8e6",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
        />
        <path
          id="patch_17"
          d="M120 353.7h495.278v-69.3H120z"
          clipPath="url(#p4433d6cd14)"
          style={{
            fill: "#393e46",
            opacity: 0.3,
            stroke: "#000",
            strokeLinejoin: "miter",
          }}
  onMouseEnter={(e) =>
    handleMouseEnter(
      e,
"<strong>ORCA</strong>\n"+ 
"\n"+
"<strong>Description</strong>:\n"+
"Strong capabilities to slice topics based on the user's specific needs, providing a flexible approach with unmatched precision and recall.\n"+
"\n"+
"<strong>Drawbacks</strong>:\n"+
"- Requires contextual understanding of the subject matter to act on surfaced patterns.\n"

	  
    )
  }
  onMouseLeave={handleMouseLeave}		  
        />
        <path
          id="patch_18"
          d="M28.461 561.6V7.2"
          style={{
            fill: "none",
            stroke: "#262626",
            strokeWidth: 1.25,
            strokeLinejoin: "miter",
            strokeLinecap: "square",
          }}
        />
        <path
          id="patch_19"
          d="M850.005 561.6V7.2"
          style={{
            fill: "none",
            stroke: "#262626",
            strokeWidth: 1.25,
            strokeLinejoin: "miter",
            strokeLinecap: "square",
          }}
        />
        <path
          id="patch_20"
          d="M28.461 561.6h821.544"
          style={{
            fill: "none",
            stroke: "#262626",
            strokeWidth: 1.25,
            strokeLinejoin: "miter",
            strokeLinecap: "square",
          }}
        />
        <path
          id="patch_21"
          d="M28.461 7.2h821.544"
          style={{
            fill: "none",
            stroke: "#262626",
            strokeWidth: 1.25,
            strokeLinejoin: "miter",
            strokeLinecap: "square",
          }}
        />
        <g
          id="text_2"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.1 0 0 -.1 57.025 545.767)"
        >
          <defs>
            <path
              id="Arial-BoldMT-45"
              d="M466 0v4581h3397v-775H1391V2791h2300v-772H1391V772h2559V0H466z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-43"
              d="m3397 1684 897-284q-206-750-686-1114T2391-78q-913 0-1501 623-587 624-587 1705 0 1144 590 1776 591 633 1554 633 841 0 1366-496 312-294 468-844l-915-219q-82 356-340 562-257 207-626 207-509 0-827-366-317-365-317-1184 0-869 312-1238 313-368 813-368 369 0 634 234 266 234 382 737z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-41"
              d="M4597 0H3591l-400 1041H1359L981 0H0l1784 4581h979L4597 0zM2894 1813l-631 1700-619-1700h1250z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#Arial-BoldMT-45" />
          <use xlinkHref="#Arial-BoldMT-43" x={66.699} />
          <use xlinkHref="#Arial-BoldMT-41" x={138.916} />
        </g>
        <g
          id="text_3"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.1 0 0 -.1 161.711 545.767)"
        >
          <defs>
            <path
              id="Arial-BoldMT-46"
              d="M472 0v4581h3141v-775H1397V2722h1912v-775H1397V0H472z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-69"
              d="M459 3769v812h879v-812H459zM459 0v3319h879V0H459z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-72"
              d="M1300 0H422v3319h816v-472q209 334 376 440 167 107 380 107 300 0 578-166l-272-765q-222 143-412 143-185 0-313-102-128-101-202-367-73-265-73-1112V0z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-73"
              d="m150 947 881 134q57-256 228-389 172-133 482-133 340 0 512 125 116 88 116 235 0 100-63 165-65 63-293 116-1063 234-1347 428-394 269-394 747 0 431 340 725 341 294 1057 294 681 0 1012-222 332-222 457-656l-829-153q-53 193-202 296-148 104-423 104-346 0-496-97-100-69-100-178 0-94 87-160 119-87 820-247 702-159 980-390 275-235 275-653 0-457-381-785T1741-75q-678 0-1074 275-395 275-517 747z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-74"
              d="M1981 3319v-700h-600V1281q0-406 17-473 18-67 79-111t148-44q122 0 353 85l75-682Q1747-75 1359-75q-237 0-428 79-190 80-279 207T528 553q-28 153-28 619v1447H97v700h403v659l881 513V3319h600z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-2d"
              d="M359 1222v878h1725v-878H359z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-50"
              d="M466 0v4581h1484q844 0 1100-68 394-104 659-449 266-345 266-892 0-422-153-710-153-287-389-451t-480-217q-331-66-959-66h-603V0H466zm925 3806V2506h506q547 0 731 72 185 72 289 225 105 153 105 356 0 250-147 412-147 163-372 204-165 31-665 31h-447z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-61"
              d="m1116 2306-797 144q134 481 462 712 328 232 975 232 588 0 875-139 288-139 405-353t117-786l-9-1025q0-438 42-646 42-207 158-445h-869q-34 88-84 259-22 79-32 104-225-219-481-329-256-109-547-109-512 0-808 278-295 278-295 703 0 282 134 502 135 220 377 337 242 118 699 205 615 116 853 216v87q0 253-125 361t-472 108q-235 0-366-92t-212-324zm1175-712q-169-56-535-135-365-78-478-153-172-122-172-309 0-184 137-319 138-134 351-134 237 0 453 156 159 119 209 291 35 112 35 428v175z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-52"
              d="M469 0v4581h1947q734 0 1067-124 333-123 533-439 200-315 200-721 0-516-304-852-303-336-906-423 300-175 495-385 196-209 527-743L4588 0H3481l-668 997q-357 534-488 673t-278 191q-147 52-466 52h-187V0H469zm925 2644h684q666 0 831 56 166 56 260 193 94 138 94 345 0 231-124 373-123 142-348 180-113 15-675 15h-722V2644z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-65"
              d="m2381 1056 875-147q-168-481-533-733-364-251-910-251-866 0-1282 566-328 453-328 1143 0 825 431 1292 432 468 1091 468 741 0 1169-489t409-1499H1103q10-390 213-608 203-217 506-217 206 0 346 112 141 113 213 363zm50 888q-9 381-197 579-187 199-456 199-287 0-475-209-187-210-184-569h1312z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-76"
              d="M1372 0 34 3319h922l625-1694 182-566q71 216 90 285 44 140 94 281l631 1694h903L2163 0h-791z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-77"
              d="M1078 0 28 3319h853l622-2175 572 2175h847l553-2175 634 2175h866L3909 0h-843l-572 2134L1931 0h-853z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#Arial-BoldMT-46" />
          <use xlinkHref="#Arial-BoldMT-69" x={61.084} />
          <use xlinkHref="#Arial-BoldMT-72" x={88.867} />
          <use xlinkHref="#Arial-BoldMT-73" x={127.783} />
          <use xlinkHref="#Arial-BoldMT-74" x={183.398} />
          <use xlinkHref="#Arial-BoldMT-2d" x={216.699} />
          <use xlinkHref="#Arial-BoldMT-50" x={250} />
          <use xlinkHref="#Arial-BoldMT-61" x={316.699} />
          <use xlinkHref="#Arial-BoldMT-73" x={372.314} />
          <use xlinkHref="#Arial-BoldMT-73" x={427.93} />
          <use xlinkHref="#Arial-BoldMT-20" x={483.545} />
          <use xlinkHref="#Arial-BoldMT-52" x={511.328} />
          <use xlinkHref="#Arial-BoldMT-65" x={583.545} />
          <use xlinkHref="#Arial-BoldMT-76" x={639.16} />
          <use xlinkHref="#Arial-BoldMT-69" x={694.775} />
          <use xlinkHref="#Arial-BoldMT-65" x={722.559} />
          <use xlinkHref="#Arial-BoldMT-77" x={778.174} />
        </g>
        <g
          id="text_4"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.1 0 0 -.1 369.654 545.767)"
        >
          <defs>
            <path
              id="Arial-BoldMT-53"
              d="m231 1491 900 87q82-453 330-666 248-212 670-212 447 0 673 189 227 189 227 442 0 163-95 277t-333 198q-162 57-740 200-744 185-1044 453-422 379-422 922 0 350 198 655 199 305 572 464 374 159 902 159 862 0 1298-378t458-1009l-925-41q-59 353-255 508-195 155-586 155-403 0-631-166-147-106-147-284 0-163 138-278 175-147 850-307 675-159 998-330 324-170 506-465 183-295 183-730 0-393-219-737-218-344-618-511T2122-81q-869 0-1335 401-465 402-556 1171z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-63"
              d="m3353 2338-865-157q-44 260-199 391t-401 131q-329 0-524-227-195-226-195-757 0-591 198-835 199-243 533-243 250 0 409 142 160 142 225 489l863-147q-134-594-516-897Q2500-75 1859-75q-728 0-1161 459-432 460-432 1272 0 822 434 1280t1175 458q606 0 964-261t514-795z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-6f"
              d="M256 1706q0 438 216 847 216 410 611 625 395 216 883 216 753 0 1234-489t481-1236q0-753-486-1249Q2709-75 1972-75q-456 0-870 206-414 207-630 605t-216 970zm900-47q0-493 234-756 235-262 579-262t576 262q233 263 233 763 0 487-233 749-232 263-576 263t-579-263q-234-262-234-756z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-6e"
              d="M3478 0h-878v1694q0 537-56 695t-183 245q-127 88-305 88-228 0-409-125t-249-332q-67-206-67-762V0H453v3319h816v-488q434 563 1094 563 290 0 530-105 241-105 364-268 124-162 172-368 49-206 49-590V0z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-64"
              d="M3503 0h-815v488q-204-285-481-424-276-139-557-139-572 0-980 461-407 461-407 1286 0 844 396 1283 397 439 1004 439 556 0 962-463v1650h878V0zM1159 1731q0-531 147-768 213-344 594-344 303 0 515 257 213 258 213 771 0 572-206 823-206 252-528 252-313 0-524-249-211-248-211-742z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#Arial-BoldMT-53" />
          <use xlinkHref="#Arial-BoldMT-65" x={66.699} />
          <use xlinkHref="#Arial-BoldMT-63" x={122.314} />
          <use xlinkHref="#Arial-BoldMT-6f" x={177.93} />
          <use xlinkHref="#Arial-BoldMT-6e" x={239.014} />
          <use xlinkHref="#Arial-BoldMT-64" x={300.098} />
          <use xlinkHref="#Arial-BoldMT-2d" x={361.182} />
          <use xlinkHref="#Arial-BoldMT-50" x={394.482} />
          <use xlinkHref="#Arial-BoldMT-61" x={461.182} />
          <use xlinkHref="#Arial-BoldMT-73" x={516.797} />
          <use xlinkHref="#Arial-BoldMT-73" x={572.412} />
          <use xlinkHref="#Arial-BoldMT-20" x={628.027} />
          <use xlinkHref="#Arial-BoldMT-52" x={655.811} />
          <use xlinkHref="#Arial-BoldMT-65" x={728.027} />
          <use xlinkHref="#Arial-BoldMT-76" x={783.643} />
          <use xlinkHref="#Arial-BoldMT-69" x={839.258} />
          <use xlinkHref="#Arial-BoldMT-65" x={867.041} />
          <use xlinkHref="#Arial-BoldMT-77" x={922.656} />
        </g>
        <g
          id="text_5"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.1 0 0 -.1 559.61 545.635)"
        >
          <defs>
            <path
              id="Arial-BoldMT-51"
              d="M4153 581q341-243 741-387l-341-653q-209 62-409 171-44 22-616 407-450-197-997-197-1056 0-1655 622-598 622-598 1747 0 1122 600 1745t1628 623q1019 0 1616-623t597-1745q0-594-166-1044-125-344-400-666zm-744 522q179 210 268 506 89 297 89 682 0 793-350 1185-350 393-916 393t-918-394q-351-394-351-1184 0-803 351-1202 352-398 890-398 200 0 378 65-281 185-572 288l260 528q456-156 871-469z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-75"
              d="M2644 0v497q-181-266-477-419-295-153-623-153-335 0-601 147-265 147-384 412-118 266-118 735v2100h878V1794q0-700 48-858 49-158 177-250t325-92q225 0 403 123 178 124 243 306 66 183 66 896v1400h878V0h-815z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-6c"
              d="M459 0v4581h879V0H459z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-79"
              d="M44 3319h934l794-2356 775 2356h909L2284 125l-209-578q-116-291-221-444-104-153-240-248-136-96-335-149-198-53-448-53-253 0-497 53l-78 688q207-41 372-41 306 0 453 180 147 179 225 458L44 3319z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#Arial-BoldMT-51" />
          <use xlinkHref="#Arial-BoldMT-75" x={77.783} />
          <use xlinkHref="#Arial-BoldMT-61" x={138.867} />
          <use xlinkHref="#Arial-BoldMT-6c" x={194.482} />
          <use xlinkHref="#Arial-BoldMT-69" x={222.266} />
          <use xlinkHref="#Arial-BoldMT-74" x={250.049} />
          <use xlinkHref="#Arial-BoldMT-79" x={283.35} />
          <use xlinkHref="#Arial-BoldMT-20" x={338.965} />
          <use xlinkHref="#Arial-BoldMT-43" x={366.748} />
          <use xlinkHref="#Arial-BoldMT-6f" x={438.965} />
          <use xlinkHref="#Arial-BoldMT-6e" x={500.049} />
          <use xlinkHref="#Arial-BoldMT-74" x={561.133} />
          <use xlinkHref="#Arial-BoldMT-72" x={594.434} />
          <use xlinkHref="#Arial-BoldMT-6f" x={633.35} />
          <use xlinkHref="#Arial-BoldMT-6c" x={694.434} />
        </g>
        <g
          id="text_6"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.1 0 0 -.1 651.73 545.635)"
        >
          <use xlinkHref="#Arial-BoldMT-41" />
          <use xlinkHref="#Arial-BoldMT-6e" x={72.217} />
          <use xlinkHref="#Arial-BoldMT-61" x={133.301} />
          <use xlinkHref="#Arial-BoldMT-6c" x={188.916} />
          <use xlinkHref="#Arial-BoldMT-79" x={216.699} />
          <use xlinkHref="#Arial-BoldMT-74" x={272.314} />
          <use xlinkHref="#Arial-BoldMT-69" x={305.615} />
          <use xlinkHref="#Arial-BoldMT-63" x={333.398} />
          <use xlinkHref="#Arial-BoldMT-73" x={389.014} />
        </g>
        <g
          id="text_7"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.1 0 0 -.1 725.076 545.635)"
        >
          <defs>
            <path
              id="Arial-BoldMT-4e"
              d="M475 0v4581h900l1875-3059v3059h859V0h-928L1334 2988V0H475z"
              transform="scale(.01563)"
            />
            <path
              id="Arial-BoldMT-68"
              d="M1334 4581V2897q425 497 1016 497 303 0 547-113 244-112 367-287 124-175 169-388 45-212 45-659V0h-878v1753q0 522-50 662-50 141-177 224-126 83-317 83-218 0-390-107-172-106-252-320t-80-632V0H456v4581h878z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#Arial-BoldMT-4e" />
          <use xlinkHref="#Arial-BoldMT-61" x={72.217} />
          <use xlinkHref="#Arial-BoldMT-72" x={127.832} />
          <use xlinkHref="#Arial-BoldMT-72" x={166.748} />
          <use xlinkHref="#Arial-BoldMT-61" x={205.664} />
          <use xlinkHref="#Arial-BoldMT-74" x={261.279} />
          <use xlinkHref="#Arial-BoldMT-69" x={294.58} />
          <use xlinkHref="#Arial-BoldMT-76" x={322.363} />
          <use xlinkHref="#Arial-BoldMT-65" x={377.979} />
          <use xlinkHref="#Arial-BoldMT-20" x={433.594} />
          <use xlinkHref="#Arial-BoldMT-53" x={461.377} />
          <use xlinkHref="#Arial-BoldMT-79" x={528.076} />
          <use xlinkHref="#Arial-BoldMT-6e" x={583.691} />
          <use xlinkHref="#Arial-BoldMT-74" x={644.775} />
          <use xlinkHref="#Arial-BoldMT-68" x={678.076} />
          <use xlinkHref="#Arial-BoldMT-65" x={739.16} />
          <use xlinkHref="#Arial-BoldMT-73" x={794.775} />
          <use xlinkHref="#Arial-BoldMT-69" x={850.391} />
          <use xlinkHref="#Arial-BoldMT-73" x={878.174} />
        </g>
        <g id="AnnotationBbox_1">
          <image
            xlinkHref="data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAC8AAAAvCAYAAABzJ5OsAAACfUlEQVR4nNVaO1LDMBB9CtBTwRloaRgmkMlQ+Aq+RhruwTVyBVeeZJgABSV3gI4KMjCIAsuWZX1W8sY4r/HYkay3b3e1azsCjLi/gwSA6QJCXbucZRIAIAEI4PlxdbTdfn5zrHfYZ7IiS0JlzvnF7Eu/vFkVwjacgiTyUaQDqDzztlkVp7Fzo8hzkubAhDpwbMQBgvIspKtk5YZXeTa1d0Ac8JAfY5iYsJLfB+JARMKOEZ2E3anq7sQ9qSuxZ55Z0FrKcxDXW4MOUhNXAJBaq1GBNWx8xHup4vBYTb6P6tMFhFdx+9oNMf0YmKyr34r52Fpycwux/QqP80IYxwhMgEZ1ynxl9nTBQDwRSv3orvIqEB5UeL1s/OgaOwHqRHv3LUaJ6xjEJIhrbJ2w0wWOXeQ4SXNi56SsxUfFQXN826ybh5HL60ySw2Yo1FboO4yF2WbdrqRCTdZlkAOTt7rZ4fvOs60wxoo9b8yGIR+qoom1fRjyoSqauG0MGzaUPiYCw5Lv0cfYDN+fhLUY3ultyjx7BXCizufL9NdxPkgJCOKdzVIgATysCtEiX+aZNAeW+V+F5DaCShzoRpk6PwQagraBCrsyggSznahgjXnfZlDmmSzz7KUXEcpCOhyJPgG6ahKkPdO9lYxqIfKNqoGqdei121ReiDPCogz5qd2mPNAvlpOMAMKSWxjpDRvrPs/hhRi0yHPsJCy5YEC18t43ZsA/bYUBCPwVJfP6/rQHFljJj0191xdDp/LKgP9+Ue/71OkNm/myiGlB2BH6RhuM+fmyEGMLIwVywo7RgKjdZmxeSPp8rwzgKEiD//dAwfQCxZjnp/XB9vPjp8+6Cr+E+N3pcNyYcQAAAABJRU5ErkJggg=="
            id="image267aa103c4"
            width={33.84}
            height={33.84}
            x={481.235}
            y={-301.88}
            transform="matrix(1 0 0 -1 0 33.84)"
          />
        </g>
        <g id="text_8">
          <g
            style={{
              fill: "#262626",
            }}
            transform="matrix(.09 0 0 -.09 149.737 196.52)"
          >
            <defs>
              <path
                id="ArialMT-52"
                d="M503 0v4581h2031q613 0 931-124 319-123 510-436 191-312 191-690 0-487-316-822-316-334-975-425 241-115 366-228 265-243 503-609L4541 0h-763l-606 953q-266 413-438 631-171 219-307 306-136 88-277 123-103 21-337 21h-704V0H503zm606 2559h1304q415 0 649 86 235 86 357 275t122 411q0 325-236 534-236 210-746 210H1109V2559z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-61"
                d="M2588 409q-313-265-602-375-289-109-620-109-547 0-841 267T231 875q0 244 111 445 111 202 291 324t405 184q165 44 500 85 681 81 1003 193 3 116 3 147 0 344-160 485-215 190-640 190-397 0-586-139t-280-492l-550 75q75 353 247 570t497 334q325 118 753 118 425 0 690-100 266-100 391-252 125-151 175-383 28-143 28-518v-750q0-785 36-993 36-207 143-398h-588q-87 175-112 409zm-47 1257q-307-125-919-213-347-50-491-113-143-62-222-182-78-120-78-267 0-225 170-375 171-150 499-150 325 0 578 142t372 389q91 191 91 562v207z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-69"
                d="M425 3934v647h563v-647H425zM425 0v3319h563V0H425z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-76"
                d="M1344 0 81 3319h594l713-1988q115-322 212-668 75 262 209 631l738 2025h578L1869 0h-525z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-41"
                d="m-9 0 1759 4581h653L4278 0h-690l-535 1388H1138L634 0H-9zm1322 1881h1553l-478 1269q-219 578-325 950-88-441-247-875l-503-1344z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-6e"
                d="M422 0v3319h506v-472q366 547 1056 547 300 0 552-108t377-283q125-175 175-415 31-157 31-547V0h-563v2019q0 344-66 514-65 170-232 271-167 102-392 102-360 0-621-228t-261-865V0H422z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-63"
                d="m2588 1216 553-72q-91-572-465-896-373-323-917-323-681 0-1095 445-414 446-414 1277 0 537 178 940 178 404 542 605 364 202 793 202 540 0 884-274 344-273 441-776l-547-85q-78 335-277 503-198 169-480 169-425 0-691-305-265-304-265-963 0-669 256-972 257-303 669-303 331 0 553 203t282 625z"
                transform="scale(.01563)"
              />
            </defs>
            <use xlinkHref="#ArialMT-52" />
            <use xlinkHref="#ArialMT-65" x={72.217} />
            <use xlinkHref="#ArialMT-6c" x={127.832} />
            <use xlinkHref="#ArialMT-61" x={150.049} />
            <use xlinkHref="#ArialMT-74" x={205.664} />
            <use xlinkHref="#ArialMT-69" x={233.447} />
            <use xlinkHref="#ArialMT-76" x={255.664} />
            <use xlinkHref="#ArialMT-69" x={305.664} />
            <use xlinkHref="#ArialMT-74" x={327.881} />
            <use xlinkHref="#ArialMT-79" x={355.664} />
            <use xlinkHref="#ArialMT-20" x={405.664} />
            <use xlinkHref="#ArialMT-41" x={427.947} />
            <use xlinkHref="#ArialMT-6e" x={494.646} />
            <use xlinkHref="#ArialMT-61" x={550.262} />
            <use xlinkHref="#ArialMT-6c" x={605.877} />
            <use xlinkHref="#ArialMT-79" x={628.094} />
            <use xlinkHref="#ArialMT-74" x={678.094} />
            <use xlinkHref="#ArialMT-69" x={705.877} />
            <use xlinkHref="#ArialMT-63" x={728.094} />
            <use xlinkHref="#ArialMT-73" x={778.094} />
          </g>
          <g
            style={{
              fill: "#262626",
            }}
            transform="matrix(.09 0 0 -.09 149.737 206.276)"
          >
            <defs>
              <path
                id="ArialMT-54"
                d="M1659 0v4041H150v540h3631v-540H2266V0h-607z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-31"
                d="M2384 0h-562v3584q-203-193-533-387t-592-291v544q472 222 825 537 353 316 500 613h362V0z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-2e"
                d="M581 0v641h641V0H581z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-30"
                d="M266 2259q0 813 167 1308 167 496 496 764 330 269 830 269 369 0 647-149 278-148 459-428 182-279 285-681 103-401 103-1083 0-806-166-1301-165-495-495-766-329-270-833-270-662 0-1040 475-453 572-453 1862zm578 0q0-1128 264-1502 264-373 651-373 388 0 652 375t264 1500q0 1132-264 1503-264 372-658 372-387 0-619-328-290-418-290-1547z"
                transform="scale(.01563)"
              />
            </defs>
            <use xlinkHref="#ArialMT-28" />
            <use xlinkHref="#ArialMT-54" x={33.301} />
            <use xlinkHref="#ArialMT-41" x={87.01} />
            <use xlinkHref="#ArialMT-52" x={153.709} />
            <use xlinkHref="#ArialMT-20" x={225.926} />
            <use xlinkHref="#ArialMT-31" x={253.709} />
            <use xlinkHref="#ArialMT-2e" x={309.324} />
            <use xlinkHref="#ArialMT-30" x={337.107} />
            <use xlinkHref="#ArialMT-29" x={392.723} />
          </g>
        </g>
        <g id="text_9">
          <g
            style={{
              fill: "#262626",
            }}
            transform="matrix(.09 0 0 -.09 267.1 231.17)"
          >
            <defs>
              <path
                id="ArialMT-4c"
                d="M469 0v4581h606V541h2256V0H469z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-72"
                d="M416 0v3319h506v-503q194 353 358 465 164 113 361 113 284 0 578-181l-194-522q-206 122-412 122-185 0-332-111t-209-308q-94-300-94-656V0H416z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-67"
                d="m319-275 547-81q34-253 190-369 210-156 572-156 391 0 603 156 213 156 288 437 44 172 40 722Q2191 0 1641 0 956 0 581 494T206 1678q0 475 172 876 172 402 498 621 327 219 768 219 587 0 969-475v400h518V450q0-775-158-1098-157-324-500-511-342-188-842-188-593 0-959 267T319-275zm465 1994q0-653 259-953 260-300 651-300 387 0 649 298 263 299 263 936 0 609-270 918-270 310-652 310-375 0-638-305-262-304-262-904z"
                transform="scale(.01563)"
              />
            </defs>
            <use xlinkHref="#ArialMT-52" />
            <use xlinkHref="#ArialMT-65" x={72.217} />
            <use xlinkHref="#ArialMT-6c" x={127.832} />
            <use xlinkHref="#ArialMT-61" x={150.049} />
            <use xlinkHref="#ArialMT-74" x={205.664} />
            <use xlinkHref="#ArialMT-69" x={233.447} />
            <use xlinkHref="#ArialMT-76" x={255.664} />
            <use xlinkHref="#ArialMT-69" x={305.664} />
            <use xlinkHref="#ArialMT-74" x={327.881} />
            <use xlinkHref="#ArialMT-79" x={355.664} />
            <use xlinkHref="#ArialMT-20" x={405.664} />
            <use xlinkHref="#ArialMT-41" x={427.947} />
            <use xlinkHref="#ArialMT-63" x={494.646} />
            <use xlinkHref="#ArialMT-74" x={544.646} />
            <use xlinkHref="#ArialMT-69" x={572.43} />
            <use xlinkHref="#ArialMT-76" x={594.646} />
            <use xlinkHref="#ArialMT-65" x={644.646} />
            <use xlinkHref="#ArialMT-20" x={700.262} />
            <use xlinkHref="#ArialMT-4c" x={728.045} />
            <use xlinkHref="#ArialMT-65" x={783.66} />
            <use xlinkHref="#ArialMT-61" x={839.275} />
            <use xlinkHref="#ArialMT-72" x={894.891} />
            <use xlinkHref="#ArialMT-6e" x={928.191} />
            <use xlinkHref="#ArialMT-69" x={983.807} />
            <use xlinkHref="#ArialMT-6e" x={1006.023} />
            <use xlinkHref="#ArialMT-67" x={1061.639} />
          </g>
          <g
            style={{
              fill: "#262626",
            }}
            transform="matrix(.09 0 0 -.09 267.1 240.926)"
          >
            <defs>
              <path
                id="ArialMT-32"
                d="M3222 541V0H194q-6 203 65 391 116 309 370 609 255 300 737 694 747 612 1009 970 263 358 263 677 0 334-240 563-239 230-623 230-406 0-650-244-244-243-247-674l-578 59q59 647 446 986 388 339 1042 339 659 0 1043-366 385-365 385-906 0-275-113-541-112-265-373-559t-867-806q-507-425-651-577-143-151-237-304h2247z"
                transform="scale(.01563)"
              />
            </defs>
            <use xlinkHref="#ArialMT-28" />
            <use xlinkHref="#ArialMT-54" x={33.301} />
            <use xlinkHref="#ArialMT-41" x={87.01} />
            <use xlinkHref="#ArialMT-52" x={153.709} />
            <use xlinkHref="#ArialMT-20" x={225.926} />
            <use xlinkHref="#ArialMT-32" x={253.709} />
            <use xlinkHref="#ArialMT-2e" x={309.324} />
            <use xlinkHref="#ArialMT-30" x={337.107} />
            <use xlinkHref="#ArialMT-29" x={392.723} />
          </g>
        </g>
        <g
          id="text_10"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.09 0 0 -.09 188.858 414.281)"
        >
          <defs>
            <path
              id="ArialMT-42"
              d="M469 0v4581h1719q525 0 842-139t496-428q180-289 180-605 0-293-159-553-159-259-481-418 415-122 638-416 224-294 224-694 0-322-136-599-136-276-336-426T2954 76Q2653 0 2216 0H469zm606 2656h991q403 0 578 53 231 69 348 228 117 160 117 401 0 228-109 401-109 174-313 238-203 64-696 64h-916V2656zm0-2115h1141q293 0 412 22 210 37 350 124 141 88 231 255 91 167 91 386 0 256-131 445-131 190-364 266-233 77-671 77H1075V541z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#ArialMT-42" />
          <use xlinkHref="#ArialMT-72" x={66.699} />
          <use xlinkHref="#ArialMT-61" x={100} />
          <use xlinkHref="#ArialMT-69" x={155.615} />
          <use xlinkHref="#ArialMT-6e" x={177.832} />
          <use xlinkHref="#ArialMT-73" x={233.447} />
          <use xlinkHref="#ArialMT-70" x={283.447} />
          <use xlinkHref="#ArialMT-61" x={339.063} />
          <use xlinkHref="#ArialMT-63" x={394.678} />
          <use xlinkHref="#ArialMT-65" x={444.678} />
        </g>
        <g
          id="text_11"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.09 0 0 -.09 149.737 275.681)"
        >
          <defs>
            <path
              id="ArialMT-49"
              d="M597 0v4581h606V0H597z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#ArialMT-52" />
          <use xlinkHref="#ArialMT-65" x={72.217} />
          <use xlinkHref="#ArialMT-76" x={127.832} />
          <use xlinkHref="#ArialMT-65" x={177.832} />
          <use xlinkHref="#ArialMT-61" x={233.447} />
          <use xlinkHref="#ArialMT-6c" x={289.063} />
          <use xlinkHref="#ArialMT-20" x={311.279} />
          <use xlinkHref="#ArialMT-41" x={333.563} />
          <use xlinkHref="#ArialMT-49" x={400.262} />
        </g>
        <g
          id="text_12"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.09 0 0 -.09 71.494 483.581)"
        >
          <defs>
            <path
              id="ArialMT-4e"
              d="M488 0v4581h621L3516 984v3597h581V0h-622L1069 3600V0H488z"
              transform="scale(.01563)"
            />
            <path
              id="ArialMT-78"
              d="m47 0 1212 1725L138 3319h703l509-778q144-222 231-372 138 206 253 365l560 785h672L1919 1756 3153 0h-690l-682 1031-181 278L728 0H47z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#ArialMT-4e" />
          <use xlinkHref="#ArialMT-75" x={72.217} />
          <use xlinkHref="#ArialMT-69" x={127.832} />
          <use xlinkHref="#ArialMT-78" x={150.049} />
        </g>
        <g
          id="text_13"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.09 0 0 -.09 110.616 448.826)"
        >
          <defs>
            <path
              id="ArialMT-6b"
              d="M425 0v4581h563V1969l1331 1350h728L1778 2088 3175 0h-694L1384 1697l-396-381V0H425z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#ArialMT-4c" />
          <use xlinkHref="#ArialMT-6f" x={55.615} />
          <use xlinkHref="#ArialMT-67" x={111.23} />
          <use xlinkHref="#ArialMT-69" x={166.846} />
          <use xlinkHref="#ArialMT-6b" x={189.063} />
          <use xlinkHref="#ArialMT-63" x={239.063} />
          <use xlinkHref="#ArialMT-75" x={289.063} />
          <use xlinkHref="#ArialMT-6c" x={344.678} />
          <use xlinkHref="#ArialMT-6c" x={366.895} />
        </g>
        <g
          id="text_14"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.09 0 0 -.09 227.979 275.681)"
        >
          <defs>
            <path
              id="ArialMT-44"
              d="M494 0v4581h1578q534 0 816-65 393-91 671-328 363-307 542-784 180-476 180-1088 0-522-122-925-121-403-312-668-191-264-418-416-226-151-546-229T2147 0H494zm606 541h978q453 0 711 84t411 238q216 215 336 579t120 883q0 719-236 1105t-573 517q-244 94-784 94h-963V541z"
              transform="scale(.01563)"
            />
            <path
              id="ArialMT-53"
              d="m288 1472 571 50q41-344 189-564 149-220 461-356 313-136 704-136 346 0 612 103t395 282q130 180 130 393 0 215-125 376t-412 271q-185 72-816 223-631 152-884 286-329 172-490 426-160 255-160 571 0 347 196 648 197 302 575 458 379 156 841 156 509 0 898-164 390-164 599-483 209-318 225-721l-581-44q-47 434-318 656-270 222-798 222-550 0-802-202-251-201-251-485 0-247 178-407 175-159 914-326t1014-292q400-185 590-468 191-282 191-651 0-366-209-690-209-323-602-503-392-179-882-179-622 0-1043 181-420 181-659 545-239 365-251 824z"
              transform="scale(.01563)"
            />
            <path
              id="ArialMT-4f"
              d="M309 2231q0 1141 612 1786 613 646 1582 646 635 0 1144-304 509-303 776-845 268-542 268-1230 0-696-282-1246-281-550-797-833Q3097-78 2500-78q-647 0-1157 312-509 313-772 853-262 541-262 1144zm625-9q0-828 445-1305 446-476 1118-476 684 0 1126 481 443 481 443 1366 0 559-189 976t-554 647q-364 230-817 230-643 0-1108-443-464-442-464-1476z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#ArialMT-44" />
          <use xlinkHref="#ArialMT-49" x={72.217} />
          <use xlinkHref="#ArialMT-53" x={100} />
          <use xlinkHref="#ArialMT-43" x={166.699} />
          <use xlinkHref="#ArialMT-4f" x={238.916} />
          <use xlinkHref="#ArialMT-20" x={316.699} />
          <use xlinkHref="#ArialMT-41" x={338.982} />
          <use xlinkHref="#ArialMT-49" x={405.682} />
        </g>
        <g
          id="text_15"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.09 0 0 -.09 149.737 414.281)"
        >
          <defs>
            <path
              id="ArialMT-77"
              d="M1034 0 19 3319h581l528-1916 197-712q13 53 172 684l528 1944h578l497-1925 166-635 190 641 569 1919h547L3534 0h-584l-528 1988-128 565L1622 0h-588z"
              transform="scale(.01563)"
            />
          </defs>
          <use xlinkHref="#ArialMT-45" />
          <use xlinkHref="#ArialMT-76" x={66.699} />
          <use xlinkHref="#ArialMT-65" x={116.699} />
          <use xlinkHref="#ArialMT-72" x={172.314} />
          <use xlinkHref="#ArialMT-6c" x={205.615} />
          <use xlinkHref="#ArialMT-61" x={227.832} />
          <use xlinkHref="#ArialMT-77" x={283.447} />
        </g>
        <g
          id="text_16"
          style={{
            fill: "#262626",
          }}
          transform="matrix(.09 0 0 -.09 149.737 136.976)"
        >
          <use xlinkHref="#ArialMT-65" />
          <use xlinkHref="#ArialMT-44" x={55.615} />
          <use xlinkHref="#ArialMT-69" x={127.832} />
          <use xlinkHref="#ArialMT-73" x={150.049} />
          <use xlinkHref="#ArialMT-63" x={200.049} />
          <use xlinkHref="#ArialMT-6f" x={250.049} />
          <use xlinkHref="#ArialMT-76" x={305.664} />
          <use xlinkHref="#ArialMT-65" x={355.664} />
          <use xlinkHref="#ArialMT-72" x={411.279} />
          <use xlinkHref="#ArialMT-79" x={444.58} />
          <use xlinkHref="#ArialMT-20" x={494.58} />
          <use xlinkHref="#ArialMT-41" x={516.863} />
          <use xlinkHref="#ArialMT-49" x={583.563} />
        </g>
        <g id="legend_1">
          <path
            id="patch_22"
            d="M39.261 26.736h24v-8.4h-24z"
            style={{
              fill: "#c05746",
              opacity: 0.3,
            }}
          />
          <g
            id="text_17"
            style={{
              fill: "#262626",
            }}
            transform="matrix(.12 0 0 -.12 72.861 26.736)"
          >
            <defs>
              <path
                id="ArialMT-4b"
                d="M469 0v4581h606V2309l2275 2272h822L2250 2725 4256 0h-800L1825 2319l-750-731V0H469z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-64"
                d="M2575 0v419Q2259-75 1647-75q-397 0-730 219T401 755q-182 392-182 901 0 497 165 902 166 405 497 620 332 216 741 216 300 0 534-127 235-126 382-329v1643h559V0h-522zM797 1656q0-637 268-953 269-315 635-315 369 0 626 301 258 302 258 920 0 682-263 1000-262 319-646 319-375 0-627-306-251-306-251-966z"
                transform="scale(.01563)"
              />
              <path
                id="ArialMT-68"
                d="M422 0v4581h562V2938q394 456 994 456 369 0 641-146 272-145 389-401t117-744V0h-562v2103q0 422-183 614t-517 192q-250 0-471-130-220-129-314-351t-94-612V0H422z"
                transform="scale(.01563)"
              />
            </defs>
            <use xlinkHref="#ArialMT-4b" />
            <use xlinkHref="#ArialMT-65" x={66.699} />
            <use xlinkHref="#ArialMT-79" x={122.314} />
            <use xlinkHref="#ArialMT-77" x={172.314} />
            <use xlinkHref="#ArialMT-6f" x={244.531} />
            <use xlinkHref="#ArialMT-72" x={300.146} />
            <use xlinkHref="#ArialMT-64" x={333.447} />
            <use xlinkHref="#ArialMT-20" x={389.063} />
            <use xlinkHref="#ArialMT-53" x={416.846} />
            <use xlinkHref="#ArialMT-65" x={483.545} />
            <use xlinkHref="#ArialMT-61" x={539.16} />
            <use xlinkHref="#ArialMT-72" x={594.775} />
            <use xlinkHref="#ArialMT-63" x={628.076} />
            <use xlinkHref="#ArialMT-68" x={678.076} />
          </g>
          <path
            id="patch_23"
            d="M39.261 43.997h24v-8.4h-24z"
            style={{
              fill: "#c59000",
              opacity: 0.3,
            }}
          />
          <g
            id="text_18"
            style={{
              fill: "#262626",
            }}
            transform="matrix(.12 0 0 -.12 72.861 43.997)"
          >
            <use xlinkHref="#ArialMT-43" />
            <use xlinkHref="#ArialMT-6f" x={72.217} />
            <use xlinkHref="#ArialMT-6e" x={127.832} />
            <use xlinkHref="#ArialMT-63" x={183.447} />
            <use xlinkHref="#ArialMT-65" x={233.447} />
            <use xlinkHref="#ArialMT-70" x={289.063} />
            <use xlinkHref="#ArialMT-74" x={344.678} />
            <use xlinkHref="#ArialMT-75" x={372.461} />
            <use xlinkHref="#ArialMT-61" x={428.076} />
            <use xlinkHref="#ArialMT-6c" x={483.691} />
            <use xlinkHref="#ArialMT-20" x={505.908} />
            <use xlinkHref="#ArialMT-53" x={533.691} />
            <use xlinkHref="#ArialMT-65" x={600.391} />
            <use xlinkHref="#ArialMT-61" x={656.006} />
            <use xlinkHref="#ArialMT-72" x={711.621} />
            <use xlinkHref="#ArialMT-63" x={744.922} />
            <use xlinkHref="#ArialMT-68" x={794.922} />
          </g>
          <path
            id="patch_24"
            d="M198.92 26.736h24v-8.4h-24z"
            style={{
              fill: "#90ee90",
              opacity: 0.3,
            }}
          />
          <g
            id="text_19"
            style={{
              fill: "#262626",
            }}
            transform="matrix(.12 0 0 -.12 232.52 26.736)"
          >
            <defs>
              <path
                id="ArialMT-4d"
                d="M475 0v4581h913l1084-3243q150-454 219-679 78 250 243 735l1097 3187h816V0h-584v3834L2931 0h-547L1059 3900V0H475z"
                transform="scale(.01563)"
              />
            </defs>
            <use xlinkHref="#ArialMT-53" />
            <use xlinkHref="#ArialMT-75" x={66.699} />
            <use xlinkHref="#ArialMT-70" x={122.314} />
            <use xlinkHref="#ArialMT-65" x={177.93} />
            <use xlinkHref="#ArialMT-72" x={233.545} />
            <use xlinkHref="#ArialMT-76" x={266.846} />
            <use xlinkHref="#ArialMT-69" x={316.846} />
            <use xlinkHref="#ArialMT-73" x={339.063} />
            <use xlinkHref="#ArialMT-65" x={389.063} />
            <use xlinkHref="#ArialMT-64" x={444.678} />
            <use xlinkHref="#ArialMT-20" x={500.293} />
            <use xlinkHref="#ArialMT-4d" x={528.076} />
            <use xlinkHref="#ArialMT-4c" x={611.377} />
          </g>
          <path
            id="patch_25"
            d="M198.92 43.856h24v-8.4h-24z"
            style={{
              fill: "#f7f7f7",
              opacity: 0.3,
            }}
          />
          <g
            id="text_20"
            style={{
              fill: "#262626",
            }}
            transform="matrix(.12 0 0 -.12 232.52 43.856)"
          >
            <use xlinkHref="#ArialMT-43" />
            <use xlinkHref="#ArialMT-6f" x={72.217} />
            <use xlinkHref="#ArialMT-6e" x={127.832} />
            <use xlinkHref="#ArialMT-74" x={183.447} />
            <use xlinkHref="#ArialMT-69" x={211.23} />
            <use xlinkHref="#ArialMT-6e" x={233.447} />
            <use xlinkHref="#ArialMT-75" x={289.063} />
            <use xlinkHref="#ArialMT-6f" x={344.678} />
            <use xlinkHref="#ArialMT-75" x={400.293} />
            <use xlinkHref="#ArialMT-73" x={455.908} />
            <use xlinkHref="#ArialMT-20" x={505.908} />
            <use xlinkHref="#ArialMT-41" x={528.191} />
            <use xlinkHref="#ArialMT-63" x={594.891} />
            <use xlinkHref="#ArialMT-74" x={644.891} />
            <use xlinkHref="#ArialMT-69" x={672.674} />
            <use xlinkHref="#ArialMT-76" x={694.891} />
            <use xlinkHref="#ArialMT-65" x={744.891} />
            <use xlinkHref="#ArialMT-20" x={800.506} />
            <use xlinkHref="#ArialMT-4c" x={828.289} />
            <use xlinkHref="#ArialMT-65" x={883.904} />
            <use xlinkHref="#ArialMT-61" x={939.52} />
            <use xlinkHref="#ArialMT-72" x={995.135} />
            <use xlinkHref="#ArialMT-6e" x={1028.436} />
            <use xlinkHref="#ArialMT-69" x={1084.051} />
            <use xlinkHref="#ArialMT-6e" x={1106.268} />
            <use xlinkHref="#ArialMT-67" x={1161.883} />
            <use xlinkHref="#ArialMT-20" x={1217.498} />
            <use xlinkHref="#ArialMT-28" x={1245.281} />
            <use xlinkHref="#ArialMT-43" x={1278.582} />
            <use xlinkHref="#ArialMT-41" x={1350.799} />
            <use xlinkHref="#ArialMT-4c" x={1417.498} />
            <use xlinkHref="#ArialMT-29" x={1473.113} />
          </g>
          <path
            id="patch_26"
            d="M437.279 26.736h24v-8.4h-24z"
            style={{
              fill: "#add8e6",
              opacity: 0.3,
            }}
          />
          <g
            id="text_21"
            style={{
              fill: "#262626",
            }}
            transform="matrix(.12 0 0 -.12 470.879 26.736)"
          >
            <defs>
              <path
                id="ArialMT-47"
                d="M2638 1797v537l1940 4V638q-447-357-922-537-475-179-975-179-675 0-1227 289-551 289-832 836T341 2269q0 669 279 1248 280 580 805 861t1209 281q497 0 898-161 402-160 630-448 229-287 347-750l-546-150q-104 350-257 550t-438 320q-284 121-630 121-416 0-719-127-303-126-489-333-186-206-289-453-175-425-175-922 0-612 211-1025 211-412 614-612t856-200q394 0 769 151 375 152 568 324v853H2638z"
                transform="scale(.01563)"
              />
            </defs>
            <use xlinkHref="#ArialMT-47" />
            <use xlinkHref="#ArialMT-65" x={77.783} />
            <use xlinkHref="#ArialMT-6e" x={133.398} />
            <use xlinkHref="#ArialMT-41" x={189.014} />
            <use xlinkHref="#ArialMT-49" x={255.713} />
          </g>
          <path
            id="patch_27"
            d="M437.279 43.71h24v-8.4h-24z"
            style={{
              fill: "#393e46",
              opacity: 0.3,
            }}
          />
          <g
            id="text_22"
            style={{
              fill: "#262626",
            }}
            transform="matrix(.12 0 0 -.12 470.879 43.71)"
          >
            <use xlinkHref="#ArialMT-4f" />
            <use xlinkHref="#ArialMT-52" x={77.783} />
            <use xlinkHref="#ArialMT-43" x={150} />
            <use xlinkHref="#ArialMT-41" x={222.217} />


   <g transform="scale(1, -1)">
    <circle cx={305} cy={-5} r={18} fill="#262626" />
    <text
      x={305}
      y={5}
      fontSize="30"
      fontFamily="Arial"
      textAnchor="middle"
      fill="#fff"
    >
      R
    </text>
  </g>
			
          </g>
        </g>
      </g>
    </g>
    <defs>
      <clipPath id="p4433d6cd14">
        <path d="M28.461 7.2h821.544v554.4H28.461z" />
      </clipPath>
    </defs>
  </svg>
        {tooltipVisible && (
<div
  className="tooltip-box-edis"

>
         <div dangerouslySetInnerHTML={{ __html: tooltipContent }} />

        </div>
      )}
	 </>
);};
export default MarketTools
