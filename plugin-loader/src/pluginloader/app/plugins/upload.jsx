define(
	['react', 'react-mdl', 'react-redux', 'plugins/actions', 'plugins/formatfingerprint'],
function(React, ReactMDL, ReactRedux, Actions, formatFingerPrint ) {
	class Upload extends React.Component {
		constructor(props) {
			super(props);
			this.state = {
				file: null
			}
			this.fileRef = null;
			this.formRef = null;
		}
		componentWillReceiveProps(nextProps) {
			if (this.props.uploading != nextProps.uploading) {
				if (nextProps.uploading == false && this.formRef) {
					this.formRef.reset();
					this.setState({file: null});
				}
			}
		}
		fileChanged() {
			var file = this.fileRef.files[0];
			this.setState({file: file});
		}
		render() {
			return (
				<ReactMDL.Card className={this.props.className}>
					<ReactMDL.CardTitle style={{color: '#fff', backgroundColor: '#757575'}}>Manual upload</ReactMDL.CardTitle>
					<ReactMDL.CardText>
						<p>
							Please select a plugin file and press the upload button to
							load a new plugin
						</p>
						<form ref={f => {this.formRef = f}}>
						<input type="file" onChange={() => this.fileChanged()} ref={f => {this.fileRef = f}} accept="application/zip" />
						</form>
					</ReactMDL.CardText>
					<ReactMDL.CardActions border>
						<ReactMDL.Button onClick={() => this.props.onUpload(this.state.file)} disabled={this.state.file == null}>Upload</ReactMDL.Button>
						<ReactMDL.Spinner style={{display: (this.props.uploading ? '' : 'none')}}/>
					</ReactMDL.CardActions>
				</ReactMDL.Card>
			)
		}
	}

	Upload.propTypes = {
		onUpload: React.PropTypes.func.isRequired,
		uploading: React.PropTypes.bool.isRequired,
	};
	const mapStateToProps = (state) => ({
		uploading: state.uploading,
	});
	const mapDispatchToProps = (dispatch) => ({
		onUpload: (file) => {
			dispatch(Actions.uploadPlugin(file));
		}
	});
	return ReactRedux.connect(mapStateToProps, mapDispatchToProps)(Upload);
});
